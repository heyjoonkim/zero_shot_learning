export CUDA_VISIBLE_DEVICES=0


## MODELS ##
# main_model="gpt2-xl"
# main_model="EleutherAI/gpt-neo-1.3B"
# main_model="EleutherAI/gpt-neo-2.7B"
main_path="./test_results/paper_results"

###############
## ZERO-SHOT ##
###############
seed="1"

task="sst2"
benchmark="glue"


main_model="gpt2-medium"

# Minimal template #
python transformers_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --benchmark_name $benchmark \
    --output_dir $main_path/$task/$main_model/zero_shot/minimal/ \
    --seed $seed \
    --n_samples 0 \
    --overwrite_output_dir \
        --prefix '' \
    --infix '
' \
    --postfix ''
# Minimal template #

main_model="gpt2-large"

# Minimal template #
python transformers_main.py \
    --task_name $task \
    --model_name_or_path $main_model \
    --benchmark_name $benchmark \
    --output_dir $main_path/$task/$main_model/zero_shot/minimal/ \
    --seed $seed \
    --n_samples 0 \
    --overwrite_output_dir \
        --prefix '' \
    --infix '
' \
    --postfix ''
# Minimal template #

# task="SetFit/sst5"
# benchmark="huggingface"

# # Minimal template #
# python transformers_main.py \
#     --task_name $task \
#     --model_name_or_path $main_model \
#     --benchmark_name $benchmark \
#     --output_dir $main_path/$task/$main_model/zero_shot/minimal/ \
#     --seed $seed \
#     --n_samples 0 \
#     --overwrite_output_dir \
#         --prefix '' \
#     --infix '
# ' \
#     --postfix ''
# # Minimal template #


# task="trec"
# benchmark="huggingface"

# # Minimal template #
# python transformers_main.py \
#     --task_name $task \
#     --model_name_or_path $main_model \
#     --benchmark_name $benchmark \
#     --output_dir $main_path/$task/$main_model/zero_shot/minimal/ \
#     --seed $seed \
#     --n_samples 0 \
#     --overwrite_output_dir \
#         --prefix '' \
#     --infix '
# ' \
#     --postfix ''
# # Minimal template #



# task="ag_news"
# benchmark="huggingface"

# # Minimal template #
# python transformers_main.py \
#     --task_name $task \
#     --model_name_or_path $main_model \
#     --benchmark_name $benchmark \
#     --output_dir $main_path/$task/$main_model/zero_shot/minimal/ \
#     --seed $seed \
#     --n_samples 0 \
#     --overwrite_output_dir \
#         --prefix '' \
#     --infix '
# ' \
#     --postfix ''
# # Minimal template #