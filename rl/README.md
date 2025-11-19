# RL Training and Testing Examples

This directory contains scripts for training and evaluating RL agents.

## Quick Start

### 1. Test Random Baseline (No Training Needed)

```bash
# Headless mode - fast evaluation
python rl/test_random_policy.py --episodes 50

# With visualization - see the robot in action
python rl/test_random_policy.py --episodes 10 --render
```

### 2. Train an Agent

```bash
# Train with PPO (requires stable-baselines3)
pip install stable-baselines3

# Quick training (50k steps, ~2-3 minutes)
python rl/train_rl.py --mode sb3 --timesteps 50000

# Longer training for better results (~5-10 minutes)
python rl/train_rl.py --mode sb3 --timesteps 200000
```

This saves a model to `models/ppo_reactive_nav.zip`

### 3. Test Your Trained Agent

```bash
# Headless mode - comprehensive evaluation
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 100

# Visual mode - watch the trained agent
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --episodes 10
```

---

## Scripts Overview

### Training Scripts

#### `train_rl.py`
Full-featured training script with multiple modes.

```bash
# Random baseline
python rl/train_rl.py --mode random --episodes 20

# Train PPO agent
python rl/train_rl.py --mode sb3 --timesteps 100000 --map custom_map

# Continuous actions
python rl/train_rl.py --mode sb3 --action-type continuous --timesteps 50000
```

**Options:**
- `--mode`: `random` or `sb3`
- `--action-type`: `discrete` or `continuous`
- `--map`: Map name (e.g., `custom_map`, `mines`, `passage`)
- `--timesteps`: Training timesteps (for SB3)
- `--episodes`: Number of episodes (for random)
- `--max-steps`: Max steps per episode
- `--render`: Enable visualization (slows training)

#### `simple_rl_example.py`
Minimal example showing basic environment usage.

```bash
python rl/simple_rl_example.py
```

---

### Testing Scripts

#### `test_random_policy.py`
Test environment with random actions (no trained model needed).

```bash
# Fast headless evaluation
python rl/test_random_policy.py --episodes 100 --quiet

# Visual test with rendering
python rl/test_random_policy.py --episodes 10 --render --fps 30

# Test on different map
python rl/test_random_policy.py --map mines --episodes 50

# Continuous actions
python rl/test_random_policy.py --action-type continuous --episodes 20
```

**Use cases:**
- Verify environment works correctly
- Establish baseline performance
- Debug rendering
- Test different maps

**Options:**
- `--episodes`: Number of test episodes
- `--map`: Map to test on
- `--action-type`: `discrete` or `continuous`
- `--render`: Enable visualization
- `--fps`: Target frames per second (if rendering)
- `--quiet`: Suppress per-episode output
- `--seed`: Random seed for reproducibility

#### `test_policy_headless.py`
Evaluate trained model without visualization (fast).

```bash
# Basic evaluation
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 100

# Test on different map
python rl/test_policy_headless.py --model models/my_model.zip --map mines --episodes 50

# Stochastic policy (with exploration)
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --stochastic --episodes 100

# Quiet mode (no per-episode output)
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 100 --quiet
```

**Options:**
- `--model`: Path to trained model (required)
- `--episodes`: Number of evaluation episodes
- `--map`: Map to evaluate on
- `--action-type`: `discrete` or `continuous`
- `--max-steps`: Max steps per episode
- `--stochastic`: Use stochastic policy
- `--quiet`: Suppress per-episode output
- `--seed`: Random seed

**Output:**
```
======================================================================
EVALUATION STATISTICS
======================================================================
Episodes:              100

OUTCOMES:
  Success Rate:         45.0%  (45/100)
  Collision Rate:       30.0%  (30/100)
  Timeout Rate:         25.0%  (25/100)

PERFORMANCE:
  Average Reward:        -0.85 ± 2.14
  Average Steps:        156.3 ± 145.2
  Steps Range:         [12, 500]
  Avg Final Distance:   145.2
======================================================================
```

#### `test_policy_visual.py`
Visualize trained model behavior in the simulator.

```bash
# Basic visualization
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --episodes 10

# Slower playback (15 FPS)
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --fps 15

# Test on different map
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --map passage --episodes 5

# Stochastic policy (see exploration behavior)
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --stochastic
```

**Options:**
- `--model`: Path to trained model (required)
- `--episodes`: Number of episodes to visualize
- `--map`: Map to use
- `--action-type`: `discrete` or `continuous`
- `--max-steps`: Max steps per episode
- `--fps`: Target frames per second (default: 30)
- `--stochastic`: Use stochastic policy
- `--seed`: Random seed

**Controls:**
- Watch the agent navigate
- Press `Ctrl+C` to stop early

---

## Typical Workflow

### 1. Baseline Evaluation
```bash
# See how random agent performs
python rl/test_random_policy.py --episodes 100 --quiet
```

Expected: ~0-5% success rate

### 2. Train Agent
```bash
# Train for 100k steps
python rl/train_rl.py --mode sb3 --timesteps 100000
```

### 3. Headless Evaluation
```bash
# Evaluate trained agent
python rl/test_policy_headless.py \
    --model models/ppo_reactive_nav.zip \
    --episodes 100
```

Expected: 30-70% success rate (depends on training time)

### 4. Visual Inspection
```bash
# Watch the agent
python rl/test_policy_visual.py \
    --model models/ppo_reactive_nav.zip \
    --episodes 10 \
    --fps 20
```

### 5. Test Generalization
```bash
# Test on different map
python rl/test_policy_headless.py \
    --model models/ppo_reactive_nav.zip \
    --map mines \
    --episodes 50
```

---

## Example Sessions

### Quick Test (2 minutes)
```bash
# Train briefly
python rl/train_rl.py --mode sb3 --timesteps 10000

# Evaluate
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 20
```

### Full Evaluation (10 minutes)
```bash
# Train properly
python rl/train_rl.py --mode sb3 --timesteps 200000

# Comprehensive evaluation
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 200

# Visual check
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --episodes 5
```

### Map Comparison
```bash
# Train on default map
python rl/train_rl.py --mode sb3 --timesteps 100000

# Test on all maps
for map in custom_map mines passage; do
    echo "Testing on $map..."
    python rl/test_policy_headless.py \
        --model models/ppo_reactive_nav.zip \
        --map $map \
        --episodes 50 \
        --quiet
done
```

---

## Troubleshooting

### Model not found
```
Error: Model file not found: models/ppo_reactive_nav.zip
```
**Solution:** Train a model first:
```bash
python rl/train_rl.py --mode sb3 --timesteps 50000
```

### ImportError: stable-baselines3
```
Error: stable-baselines3 not installed
```
**Solution:**
```bash
pip install stable-baselines3
```

### Pygame errors (for visual testing)
```
Error creating environment: ...
```
**Solution:**
```bash
pip install pygame
```

### Poor performance
If the trained agent has low success rate:
- Train longer: `--timesteps 200000` or more
- Try different hyperparameters (edit `train_rl.py`)
- Check the map is not too difficult
- Use visual testing to debug behavior

---

## Performance Expectations

| Training Steps | Expected Success Rate | Training Time |
|----------------|----------------------|---------------|
| 0 (random)     | 0-5%                | N/A           |
| 10,000         | 10-20%              | ~1 min        |
| 50,000         | 30-50%              | ~3 min        |
| 100,000        | 50-70%              | ~5 min        |
| 200,000+       | 70-90%              | ~10 min       |

*Times approximate on modern CPU, without rendering*

---

## Tips

1. **Start with headless testing** - much faster than visual
2. **Use random baseline** to verify environment works
3. **Train without rendering** - 10x faster
4. **Use visual testing** for debugging behavior
5. **Test on multiple maps** to check generalization
6. **Save models regularly** during training
7. **Use seeds** for reproducible results

---

For more details, see [RL_GUIDE.md](../RL_GUIDE.md) in the root directory.
