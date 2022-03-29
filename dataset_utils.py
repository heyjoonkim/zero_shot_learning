
#
# Utils for loading datasets from file (csv, tsv, ...).
# otherwise we use load_dataset() from huggingface library.
#

import csv

def custom_generate_dataset_dict(filename):
    input_list = []
    label_list = []
    with open(filename) as f:
        validation_lines = csv.reader(f, delimiter='\t')
        # Remove header
        next(validation_lines, None)

        for validation_line in validation_lines:
            sample_index = validation_line[0]
            label = int(validation_line[1])
            input_sentence = validation_line[2]
            generation1 = validation_line[3]
            generation2 = validation_line[4]
            generation3 = validation_line[5]

            generation = '.'.join([generation1, generation2, generation3])

            input_sentence = generation + '.' + input_sentence

            label_list.append(label)
            input_list.append(input_sentence)
            
    return_dict = {
        'sentence' : input_list,
        'label' : label_list
    }

    return return_dict

# for SST-5
def sst5_generate_dataset_dict(filename):
    input_list = []
    label_list = []
    with open(filename) as f:
        
        for line_index, line in enumerate(f):
            line = line.strip()
            comma_index = line.index(',')
            label = int(line[:comma_index])
            input_sentence = line[comma_index+1:]
            
            if input_sentence.startswith('"') and input_sentence.endswith('"'):
                input_sentence = input_sentence.replace('"', '')

            label_list.append(label)
            input_list.append(input_sentence)
    return_dict = {
        'sentence' : input_list,
        'label' : label_list
    }

    return return_dict

# for MR
def mr_generate_dataset_dict(filename):
    # same csv file format as SST-5
    return sst5_generate_dataset_dict(filename)

# for CR
def cr_generate_dataset_dict(filename):
    # same csv file format as SST-5
    return sst5_generate_dataset_dict(filename)

# for MPQA
def mpqa_generate_dataset_dict(filename):
    # same csv file format as SST-5
    return sst5_generate_dataset_dict(filename)

# for Subj
def subj_generate_dataset_dict(filename):
    # same csv file format as SST-5
    return sst5_generate_dataset_dict(filename)

# for TREC
def trec_generate_dataset_dict(filename):
    # same csv file format as SST-5
    return sst5_generate_dataset_dict(filename)


task_to_path = {
    "sst5" : {
        "train" : "/home/heyjoonkim/data/datasets/sst5/train.csv",
        "validation" : "/home/heyjoonkim/data/datasets/sst5/test.csv",
        "dataset_processor" : sst5_generate_dataset_dict,
    },
    "mr" : {
        "train" : "/home/heyjoonkim/data/datasets/mr/train.csv",
        "validation" : "/home/heyjoonkim/data/datasets/mr/test.csv",
        "dataset_processor" : mr_generate_dataset_dict,
    },
    "cr" : {
        "train" : "/home/heyjoonkim/data/datasets/cr/train.csv",
        "validation" : "/home/heyjoonkim/data/datasets/cr/test.csv",
        "dataset_processor" : cr_generate_dataset_dict,
    },
    "mpqa" : {
        "train" : "/home/heyjoonkim/data/datasets/mpqa/train.csv",
        "validation" : "/home/heyjoonkim/data/datasets/mpqa/test.csv",
        "dataset_processor" : mpqa_generate_dataset_dict,
    },
    "subj" : {
        "train" : "/home/heyjoonkim/data/datasets/subj/train.csv",
        "validation" : "/home/heyjoonkim/data/datasets/subj/test.csv",
        "dataset_processor" : subj_generate_dataset_dict,
    },
    "trec" : {
        "train" : "/home/heyjoonkim/data/datasets/trec/train.csv",
        "validation" : "/home/heyjoonkim/data/datasets/trec/test.csv",
        "dataset_processor" : trec_generate_dataset_dict,
    },
}

task_to_keys = {
    "cola": ("sentence", None),
    "mnli": ("premise", "hypothesis"),
    "mrpc": ("sentence1", "sentence2"),
    "qnli": ("question", "sentence"),
    "qqp": ("question1", "question2"),
    "rte": ("sentence1", "sentence2"),
    "sst2": ("sentence", None),
    "stsb": ("sentence1", "sentence2"),
    "wnli": ("sentence1", "sentence2"),
    "sst5": ("sentence", None),
    "mr": ("sentence", None),
    "cr": ("sentence", None),
    "mpqa": ("sentence", None),
    "subj": ("sentence", None),
    "trec": ("sentence", None),
}

task_to_verbalizer = {
    "cola": None,
    "mnli": None,
    "mrpc": None,
    "qnli": None,
    "qqp": None,
    "rte": {
        # "positive" : 0,  # entailment
        # "negative" : 1    # not entailment
        # "entailment" : 0,  # entailment
        # "not entailment" : 1    # not entailment
        # "Yes" : 0,  # entailment
        # "No" : 1    # not entailment
        "True" : 0,  # entailment
        "False" : 1    # not entailment
    },
    "sst2": None,
    "stsb": None,
    "wnli": None,
    "sst5": None,
    "mr": None,
    "cr": None,
    "mpqa": None,
    "subj": None,
    "trec": None,
}