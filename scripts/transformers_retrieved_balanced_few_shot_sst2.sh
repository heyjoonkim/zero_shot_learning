export CUDA_VISIBLE_DEVICES=3

## TASKS ##
task='sst2'
benchmark="glue"

## INFERENCE MODELS ##
# main_model="gpt2-xl"
# main_model="EleutherAI/gpt-neo-1.3B"
# main_model="EleutherAI/gpt-neo-2.7B"
main_model="EleutherAI/gpt-j-6B"

## RETRIEVAL MODELS ##
retrieval_model="all-MiniLM-L12-v1"

## directory ##
main_path="./test_results/OURS"
dataset_path="./retrieved_datasets"

## template number ##
template="retrieval"

##############
## FEW-SHOT ##
##############
seeds="1 2 3 4 5"

n_samples="1 2 4 6 8 16"

# Manual template #
for n_sample in $n_samples; do
    for seed in $seeds; do
deepspeed transformers_generated_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --benchmark_name $benchmark \
    --ds_config ds_configs/fp16.json \
    --output_dir $main_path/$task/$main_model/$template/balanced/manual/ \
    --dataset_dir $dataset_path/$task/$retrieval_model/balanced/$seed/$n_sample/ \
    --seed $seed \
    --n_samples $n_sample \
    --balance_sample \
    --overwrite_output_dir \
    --prefix 'Question: ' \
    --infix '
Type:' \
    --postfix ''
    done
done
# Manual template #






# Minimal template #
for n_sample in $n_samples; do
    for seed in $seeds; do
deepspeed transformers_generated_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --benchmark_name $benchmark \
    --ds_config ds_configs/fp16.json \
    --output_dir $main_path/$task/$main_model/$template/balanced/minimal/ \
    --dataset_dir $dataset_path/$task/$retrieval_model/balanced/$seed/$n_sample/ \
    --seed $seed \
    --n_samples $n_sample \
    --balance_sample \
    --overwrite_output_dir \
    --prefix '' \
    --infix '
' \
    --postfix ''
    done
done
# Minimal template #
