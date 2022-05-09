export CUDA_VISIBLE_DEVICES=3

output_dir="./outputs"
main_path="./retrieved_datasets"

## TASK ##
task='sst5'
benchmark="huggingface"

## MAIN MODEL FOR RETRIEVAL ##
main_model="all-MiniLM-L12-v1"

seeds="1 2 3 4 5"
# seeds="1"
n_samples="1 2 4 6 8 16"
# n_samples="6"

for n_sample in $n_samples; do
    for seed in $seeds; do
        python transformers_retrieval_balanced.py \
            --task_name $task \
            --train_task_name $task \
            --output_dir $main_path/$task/$main_model/balanced/$seed/$n_sample \
            --model_name_or_path $main_model \
            --n_samples $n_sample \
            --overwrite_output_dir \
            --seed $seed 
    done
done

sh scripts/transformers_retrieved_balanced_few_shot_sst5.sh