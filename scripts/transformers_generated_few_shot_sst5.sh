export CUDA_VISIBLE_DEVICES=3

## TASKS ##
# task="sst2"
# task="rte"
# benchmark="glue"

# task="cb"
# benchmark="super_glue"

task="sst5"
# task="agnews"
# task="yahoo"
# task="yelp"
# task='trec'
# benchmark="huggingface"

## MODELS ##
# main_model="gpt2-xl"
# main_model="EleutherAI/gpt-neo-1.3B"
# main_model="EleutherAI/gpt-neo-2.7B"
main_model="EleutherAI/gpt-j-6B"

## directory ##
main_path="./test_results/OURS"
dataset_path="./generated_datasets"

##############
## FEW-SHOT ##
##############

seeds="1 2 3 4 5 6 7 8 9 10"
n_samples="1 2 4 8 16"

# Manual template #
for n_sample in $n_samples; do
    for seed in $seeds; do
deepspeed transformers_generated_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --ds_config ds_configs/fp16.json \
    --output_dir $main_path/$task/$main_model/template2/manual/balanced/ \
    --dataset_dir $dataset_path/$task/$main_model/template2/$seed/ \
    --seed $seed \
    --n_samples $n_sample \
    --balance_sample \
    --overwrite_output_dir \
    --prefix 'Review: ' \
    --infix '
Sentiment:' \
    --postfix ''
    done
done
# Manual template #

# Manual template #
for n_sample in $n_samples; do
    for seed in $seeds; do
deepspeed transformers_generated_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --ds_config ds_configs/fp16.json \
    --output_dir $main_path/$task/$main_model/template2/manual/random/ \
    --dataset_dir $dataset_path/$task/$main_model/template2/$seed/ \
    --seed $seed \
    --n_samples $n_sample \
    --overwrite_output_dir \
    --prefix 'Review: ' \
    --infix '
Sentiment:' \
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
    --ds_config ds_configs/fp16.json \
    --output_dir $main_path/$task/$main_model/template2/minimal/balanced/ \
    --dataset_dir $dataset_path/$task/$main_model/template2/$seed/ \
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

# Minimal template #
for n_sample in $n_samples; do
    for seed in $seeds; do
deepspeed transformers_generated_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --ds_config ds_configs/fp16.json \
    --output_dir $main_path/$task/$main_model/template2/minimal/random/ \
    --dataset_dir $dataset_path/$task/$main_model/template2/$seed/ \
    --seed $seed \
    --n_samples $n_sample \
    --overwrite_output_dir \
    --prefix '' \
    --infix '
' \
    --postfix ''
    done
done
# Minimal template #
