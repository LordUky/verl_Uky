# Path Configuration Guide

This project uses a centralized path configuration system to manage environment-specific paths. This makes it easy to deploy the project across different environments without manually changing hardcoded paths throughout the codebase.

## Quick Start

### 1. Initial Setup (First Time)

When you first clone or pull this project to a new environment:

```bash
# Copy the example configuration file
cp git_ignore.py.example git_ignore.py

# Edit git_ignore.py with your environment-specific paths
nano git_ignore.py  # or use your preferred editor
```

### 2. Configure Your Paths

Edit [git_ignore.py](git_ignore.py) and update the following key paths:

```python
# Base directory for user data and projects
USER_DATA_BASE = Path("/path/to/your/userdata")

# Base directory for models
MODEL_BASE = Path("/path/to/your/models")
```

The configuration file will automatically derive other paths from these base paths.

### 3. Verify Configuration

Run the configuration file to verify your paths:

```bash
python git_ignore.py
```

This will display all configured paths and validate that critical directories exist.

## Architecture

### Files

- **[git_ignore.py](git_ignore.py)** - Your environment-specific configuration (NOT committed to git)
- **[git_ignore.py.example](git_ignore.py.example)** - Template configuration file (committed to git)
- **[.gitignore](.gitignore)** - Updated to exclude `git_ignore.py`

### Path Variables

The configuration file provides the following path variables:

#### Base Paths
- `PROJECT_ROOT` - Auto-detected project root directory
- `USER_DATA_BASE` - Base directory for user data
- `MODEL_BASE` - Base directory for models

#### Data Paths
- `FAKE_DATASET_JSON` - Path to fake dataset JSON file
- `DATA_OUTPUT_DIR` - Directory for output data (parquet files)

#### Model Paths
- `QWEN_VL_3B_BASE` - Qwen2.5-VL-3B model base directory
- `get_latest_qwen_snapshot()` - Function to get latest model snapshot

#### Retrieval Paths (for sglang_multiturn examples)
- `RETRIEVAL_INDEX_PATH` - Retrieval index file path
- `RETRIEVAL_CORPUS_PATH` - Retrieval corpus file path

## Usage in Code

### Python Files

Import paths from `git_ignore.py`:

```python
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from git_ignore import FAKE_DATASET_JSON_STR, DATA_OUTPUT_DIR_STR
except ImportError:
    print("WARNING: git_ignore.py not found. Please configure your paths.")
    # Fallback or error handling
```

### Shell Scripts

Extract paths using Python:

```bash
# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load paths from git_ignore.py
if [ -f "$PROJECT_ROOT/git_ignore.py" ]; then
    JSON_PATH=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from git_ignore import FAKE_DATASET_JSON_STR; print(FAKE_DATASET_JSON_STR)")
    DATA_DIR=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from git_ignore import DATA_OUTPUT_DIR_STR; print(DATA_OUTPUT_DIR_STR)")
else
    echo "ERROR: git_ignore.py not found. Please copy git_ignore.py.example to git_ignore.py"
    exit 1
fi
```

## Updated Files

The following files have been updated to use the centralized configuration:

### Python Files
- [examples/data_preprocess/fake_dataset_vlm.py](examples/data_preprocess/fake_dataset_vlm.py)
- [print_data_info.py](print_data_info.py)
- [test_mcq_reward.py](test_mcq_reward.py)
- [examples/sglang_multiturn/search_r1_like/local_dense_retriever/retrieval_server.py](examples/sglang_multiturn/search_r1_like/local_dense_retriever/retrieval_server.py)

### Shell Scripts
- [examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh](examples/grpo_trainer/run_qwen2_5_vl-3b_fake_dataset.sh)
- [quick_start_fake_vlm.sh](quick_start_fake_vlm.sh)

## Deployment Workflow

### Pushing to Git

```bash
# Your git_ignore.py is automatically excluded by .gitignore
# Only git_ignore.py.example is tracked
git add .
git commit -m "Your changes"
git push
```

### Pulling to New Environment

```bash
# Pull the latest changes
git pull

# Set up configuration for this environment
cp git_ignore.py.example git_ignore.py

# Edit with environment-specific paths
nano git_ignore.py

# Verify configuration
python git_ignore.py

# You're ready to run!
./quick_start_fake_vlm.sh
```

## Benefits

1. **No Manual Path Changes** - Configure once per environment, not per file
2. **Git-Friendly** - Environment-specific config stays local
3. **Easy Deployment** - Copy, configure, run
4. **Centralized Management** - All paths in one place
5. **Type Safety** - Use Path objects in Python for robust path handling
6. **Fallback Support** - Graceful degradation if config is missing

## Troubleshooting

### "git_ignore.py not found" Error

```bash
# Make sure you're in the project root
cd /path/to/verl_Uky

# Copy the example file
cp git_ignore.py.example git_ignore.py

# Edit with your paths
nano git_ignore.py
```

### Path Validation Warnings

Run the validation:

```bash
python git_ignore.py
```

Check the output for any missing directories and update your paths accordingly.

### ImportError in Scripts

Make sure the script correctly adds the project root to `sys.path`:

```python
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from git_ignore import FAKE_DATASET_JSON_STR
```

## Example Configuration

Here's an example configuration for a typical setup:

```python
# User-specific paths
USER_DATA_BASE = Path("/gpfs/projects/p32509/userdata/username")
MODEL_BASE = Path("/home/username/models")

# These will be automatically derived:
# FAKE_DATASET_JSON = /gpfs/projects/p32509/userdata/username/world_model_vlm/benchmark/prompt/fake_dataset.json
# QWEN_VL_3B_BASE = /home/username/models/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots
```

## Questions?

If you encounter any issues with the path configuration system, please check:

1. That `git_ignore.py` exists in the project root
2. That all paths in `git_ignore.py` are correct for your environment
3. That the necessary directories exist
4. That you have read permissions for all configured paths
