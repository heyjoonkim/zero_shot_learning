#!/usr/bin/env python
# coding=utf-8
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Finetuning the library models for sequence classification on GLUE."""
# You can also adapt this script on your own text classification task. Pointers for this are left as comments.

import argparse
import logging
import os
import sys
import time
import csv
import random

import numpy as np
from tqdm.auto import tqdm
from datasets import load_dataset, DatasetDict, Dataset

from transformers import set_seed

from model_wrapper.ModelWrapper import ModelWrapper

from utils import save_config
from dataset_utils import task_to_path, task_to_keys, task_to_verbalizer
from dataset_utils import prepare_incontext_sampling, prepend_incontext_samples


logger = logging.getLogger(__name__)
def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers model on a text classification task")
    parser.add_argument(
        "--task_name",
        type=str,
        default=None,
        help="The name of the glue task to train on.",
        choices=list(task_to_keys.keys()),
    )
    parser.add_argument(
        "--benchmark_name",
        type=str,
        default=None,
        help="The name of the benchmark to train on.",
        choices=['glue', 'super_glue', 'huggingface'],
    )
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        help="Path to pretrained model or model identifier from huggingface.co/models.",
        required=True,
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default=None, 
        help="Where to store the final model."
    )
    parser.add_argument(
        '--overwrite_output_dir', 
        default=False, 
        action="store_true",
        help='Overwrite output directory.'
    )
    parser.add_argument(
        "--seed", 
        type=int, 
        default=None, 
        help="A seed for reproducible training."
    )
    
    parser.add_argument(
        "--n_samples", 
        type=int, 
        default=0, 
        help="Number of samples for in-context learning."
    )
    parser.add_argument(
        '--balance_sample', 
        default=False, 
        action="store_true",
        help='Balance samples per label for in-context learning.'
    )
    # for manual prompt #
    parser.add_argument(
        "--prefix",
        type=str,
        default='',
        help="Prefix prompt.",
    )
    parser.add_argument(
        "--infix",
        type=str,
        default='',
        help="Infix prompt.",
    )
    parser.add_argument(
        "--postfix",
        type=str,
        default='',
        help="Postfix prompt.",
    )
    # until here #
    parser.add_argument(
        "--sep",
        type=str,
        default='\n\n\n',
        help="Token seperating each samples.",
    )

    args = parser.parse_args()
    
    return args
    

def main():


    args = parse_args()


    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger.setLevel(logging.INFO)

    if args.output_dir is not None:
        if not os.path.isdir(args.output_dir):
            os.makedirs(args.output_dir, exist_ok=True)
        else:
            if not args.overwrite_output_dir:
                raise NotADirectoryError(f'Output directory {args.output_dir} exits. Exit program. (overwrite_output_dir=False)')

    logging_output_file = os.path.join(args.output_dir, "output.log")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler = logging.FileHandler(logging_output_file)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    args.verbalizer = task_to_verbalizer.get(args.task_name)

    save_config(args)

    # Set seed before initializing model.
    set_seed(args.seed)
    random.seed(args.seed)

    # In distributed training, the load_dataset function guarantee that only one local process can concurrently
    # download the dataset.
    raw_datasets = DatasetDict()
    if args.task_name is not None and args.benchmark_name is not None:
        if args.benchmark_name == 'huggingface':
            raw_train_dataset = load_dataset(args.task_name, split='train')
            raw_eval_dataset = load_dataset(args.task_name, split='test')
        else:
            # Downloading and loading a dataset from the hub.
            raw_train_dataset = load_dataset(args.benchmark_name, args.task_name, split=f'train')
            # for mnli 
            if args.task_name == "mnli":
                raw_eval_dataset = load_dataset(args.benchmark_name, args.task_name, split='validation_matched')
            else:
                raw_eval_dataset = load_dataset(args.benchmark_name, args.task_name, split=f'validation')
    # for datasets from file.
    elif args.task_name in task_to_path:
        dataset_processor = task_to_path[args.task_name]["dataset_processor"]
        train_file_path = task_to_path[args.task_name]["train"]
        validation_file_path = task_to_path[args.task_name]["validation"]

        # train set
        train_dict = dataset_processor(train_file_path)
        raw_train_dataset = Dataset.from_dict(train_dict)
        # validation set
        validation_dict = dataset_processor(validation_file_path)
        raw_eval_dataset = Dataset.from_dict(validation_dict)
    else:
        raise NotImplementedError(f'{args.task_name} task is not implemented yet.')

    raw_datasets['train'] = raw_train_dataset
    raw_datasets['validation'] = raw_eval_dataset
    
    # Labels
    if args.task_name is not None and args.benchmark_name is not None:
        if args.benchmark_name == 'huggingface':
            # TODO : fix?
            label_list = raw_datasets["train"].features["label-coarse"].names
        else:
            # label_list : ['entailment', 'not_entailment']
            label_list = raw_datasets["train"].features["label"].names
        num_labels = len(label_list)
    elif args.task_name in task_to_path:
        label_list = set(raw_datasets["train"]['label'])
        num_labels = len(label_list)
    else:
        raise NotImplementedError(f'{args.task_name} task is not implemented yet.')
    
    # load OpenAI model (set connection)
    model = ModelWrapper(args.model_name_or_path, args.task_name)

    # Preprocessing the datasets
    sentence1_key, sentence2_key = task_to_keys[args.task_name]

    label2samples, full_train_samples = prepare_incontext_sampling(
        train_samples=raw_datasets['train'],
        verbalizer=args.verbalizer,
        sentence1_key=sentence1_key,
        sentence2_key=sentence2_key,
        prefix=args.prefix,
        infix=args.infix,
        postfix=args.postfix)
    
    def preprocess_function(examples):
        # Tokenize the texts
        texts = (
            (examples[sentence1_key],) if sentence2_key is None else (examples[sentence1_key], examples[sentence2_key])
        )

        sample_num = len(texts[0])
        for sample_index in range(sample_num):
            # Tokenize the texts
            texts = (
                (examples[sentence1_key],) if sentence2_key is None else (examples[sentence1_key], examples[sentence2_key])
            )
            result = dict()
            sample_num = len(texts[0])
            result['sentence1'] = examples[sentence1_key]
            input_sentences = []

            # for single sentence tasks
            if sentence2_key is None:
                for sample_index in range(sample_num):
                    input_sentence = args.prefix + texts[0][sample_index] + args.infix + args.postfix
                    input_sentences.append(input_sentence)
            else:
                result['sentence2'] = examples[sentence2_key]
                for sample_index in range(sample_num):
                    input_sentence = args.prefix + texts[0][sample_index] + args.infix + texts[1][sample_index] + args.postfix
                    input_sentences.append(input_sentence)

            result['input_sentence'] = input_sentences
            
            # Map labels to IDs (not necessary for GLUE tasks)
            if "label" in examples:
                result["labels"] = examples["label"]
            elif 'label-coarse' in examples:
                result["labels"] = examples['label-coarse']
            else:
                raise NotImplementedError
            return result

    processed_datasets = raw_datasets.map(
        preprocess_function,
        batched=True,
        remove_columns=raw_datasets["train"].column_names,
        desc="Preparing dataset",
    )

    train_dataset = processed_datasets["train"]
    eval_dataset = processed_datasets["validation"]


    logger.info("***** Zero/Few-shot Evaluation *****")
    logger.info(f"  Num TRAIN examples = {len(train_dataset)}")
    logger.info(f"  Num EVAL  examples = {len(eval_dataset)}")
    logger.info(f"  Random Seed = {args.seed}")
    logger.info(f"  K = {args.n_samples}")
    logger.info(f"  Inference Model = {args.model_name_or_path}")

    correct_count=0
    start_time = time.time()
    ## select 
    incontext_samples, sep = prepend_incontext_samples(
        label2samples=label2samples,
        full_train_samples=full_train_samples,
        k=args.n_samples,
        balance_sample=args.balance_sample,
    )


    result_writer = os.path.join(args.output_dir, f"wrong_samples_k_{args.n_samples}_seed_{args.seed}.tsv")
    with open(result_writer, "w") as file_writer:
        tsv_writer = csv.writer(file_writer, delimiter='\t')
        tsv_writer.writerow([args.prefix, args.infix, args.postfix])
        tsv_writer.writerow(['index', 'sentence1', 'sentence2', 'prediction', 'label', 'top_logprobs'])
        for index, inputs in tqdm(enumerate(eval_dataset)):

            if args.n_samples > 0:
                inputs['input_sentence'] = incontext_samples + sep + inputs['input_sentence']

            # print(inputs['input_sentence'])
            # continue

            label = inputs['labels']
            prediction, results_dict = model.forward(**inputs)

            if prediction == label:
                correct_count += 1
            else: 
                sentence2 = inputs['sentence2'] if 'sentence2' in inputs else ''
                tsv_writer.writerow([index, inputs['sentence1'], sentence2, prediction, label, str(results_dict)])

            # TODO : removes
            # if index > 20:
            #     break
            # logger.info(f'{index} | {correct_count} / {len(eval_dataset)}')
            
        result = correct_count / len(eval_dataset) * 100
        logger.info(f'Result : {correct_count} / {len(eval_dataset)} = {result}%')

        tsv_writer.writerow([correct_count, len(eval_dataset), result])

        
    end_time = time.time()
    logger.info(f'Total time : {end_time - start_time}')

if __name__ == "__main__":
    logger.info('\nStart.')
    main()
