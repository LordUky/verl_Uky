#!/bin/bash
# Optimized training script for Qwen2.5-VL-3B-Instruct to avoid OOM
# Key optimizations:
# 1. Increased GPU memory utilization from 0.3 to 0.6
# 2. Enabled parameter offloading for actor
# 3. Enabled optimizer offloading
# 4. Reduced batch sizes
# 5. Reduced max_prompt_length to save memory
# 6. Enabled chunked prefill for better memory management

set -x

# Default engine (vllm or sglang)
ENGINE=${1:-vllm}

# Get paths from git_ignore.py
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source vLLM environment variables
source "$PROJECT_ROOT/.vllm_env"

# Source paths from Python configuration
if [ -f "$PROJECT_ROOT/git_ignore.py" ]; then
    # Extract paths using Python
    MODEL_PATH=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from git_ignore import QWEN_VL_3B_BASE_STR; print(QWEN_VL_3B_BASE_STR)")
    DATA_DIR=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from git_ignore import DATA_OUTPUT_DIR_STR; print(DATA_OUTPUT_DIR_STR)")
else
    echo "ERROR: git_ignore.py not found. Please copy git_ignore.py.example to git_ignore.py and configure your paths."
    exit 1
fi

# Find the actual snapshot directory
SNAPSHOT_DIR=$(ls -t "$MODEL_PATH" | head -1)
FULL_MODEL_PATH="$MODEL_PATH/$SNAPSHOT_DIR"

echo "Using model path: $FULL_MODEL_PATH"
echo "Using data dir: $DATA_DIR"

# Environment variables are now loaded from /root/.vllm_env
# Use sitecustomize to inject LD_LIBRARY_PATH into all Python subprocesses (Uky)
ln -sf "$PROJECT_ROOT/fix_triton_sitecustomize.py" "$PROJECT_ROOT/sitecustomize.py"  # Uky
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"  # Uky

# Training configuration with OOM optimizations
python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files=$DATA_DIR/train.parquet \
    data.val_files=$DATA_DIR/train.parquet \
    data.train_batch_size=1 \
    data.max_prompt_length=4096 \
    data.max_response_length=512 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    data.image_key=images \
    actor_rollout_ref.model.path=$FULL_MODEL_PATH \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.use_fused_kernels=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=1 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.01 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=2 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=$ENGINE \
    +actor_rollout_ref.rollout.engine_kwargs.vllm.disable_mm_preprocessor_cache=True \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
    actor_rollout_ref.rollout.enable_chunked_prefill=True \
    actor_rollout_ref.rollout.enforce_eager=False \
    actor_rollout_ref.rollout.free_cache_engine=True \
    actor_rollout_ref.rollout.n=1 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=2 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console","wandb"]' \
    trainer.project_name='verl_grpo_fake_vlm' \
    trainer.experiment_name='qwen2_5_vl_3b_spatial_reasoning_optimized' \
    trainer.n_gpus_per_node=1 \
    trainer.nnodes=1 \
    trainer.save_freq=10 \
    trainer.test_freq=5 \
    trainer.total_epochs=20
