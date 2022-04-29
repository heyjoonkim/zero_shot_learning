export CUDA_VISIBLE_DEVICES=3

# task="sst2"
# task="rte"
# benchmark="glue"

# task="cb"
# benchmark="super_glue"

# task="sst5"
# task="agnews"
# task="yahoo"
# task="yelp"
task='trec'
# benchmark="huggingface"

dataset_path="./generated_datasets"

main_model="EleutherAI/gpt-j-6B"
# main_model="text-d1avinci-002"

template="template6"
seeds="1"

for seed in $seeds; do

deepspeed generated_analysis.py \
    --task_name $task \
    --ds_config ds_configs/fp16.json \
    --dataset_dir $dataset_path/$task/$main_model/$template/$seed/ \
    --seed $seed \
    --prefix '' \
    --infix '' \
    --postfix ''

done