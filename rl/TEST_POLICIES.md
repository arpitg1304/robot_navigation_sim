# Testing RL Policies - Quick Guide

This guide shows you how to test trained RL policies with and without visualization.

## Prerequisites

```bash
# Install dependencies
pip install gymnasium stable-baselines3
```

## Step 1: Train a Model (if you don't have one)

```bash
# Quick training (~2-3 minutes)
python rl/train_rl.py --mode sb3 --timesteps 50000
```

This creates: `models/ppo_reactive_nav.zip`

## Step 2: Test Headless (Fast)

```bash
# Comprehensive evaluation - no UI
python rl/test_policy_headless.py \
    --model models/ppo_reactive_nav.zip \
    --episodes 100
```

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
  Avg Final Distance:   145.2
======================================================================
```

## Step 3: Test with Visualization

```bash
# Watch the agent navigate
python rl/test_policy_visual.py \
    --model models/ppo_reactive_nav.zip \
    --episodes 10
```

This opens a window showing the robot navigating in real-time!

**Controls:**
- Watch episodes play out
- Press `Ctrl+C` to stop

---

## No Model? Test Random Baseline

```bash
# Test without any trained model (random actions)
python rl/test_random_policy.py --episodes 50

# Or with visualization
python rl/test_random_policy.py --episodes 10 --render
```

---

## Common Options

### Headless Testing

```bash
# Test on different map
python rl/test_policy_headless.py \
    --model models/ppo_reactive_nav.zip \
    --map mines \
    --episodes 100

# Quiet mode (just show summary)
python rl/test_policy_headless.py \
    --model models/ppo_reactive_nav.zip \
    --episodes 100 \
    --quiet

# Test with exploration (stochastic policy)
python rl/test_policy_headless.py \
    --model models/ppo_reactive_nav.zip \
    --episodes 50 \
    --stochastic
```

### Visual Testing

```bash
# Slower playback
python rl/test_policy_visual.py \
    --model models/ppo_reactive_nav.zip \
    --fps 15

# Different map
python rl/test_policy_visual.py \
    --model models/ppo_reactive_nav.zip \
    --map passage \
    --episodes 5
```

---

## Understanding Results

### Success Rate
- **0-5%**: Random baseline
- **30-50%**: Basic learned policy
- **50-70%**: Good performance
- **70%+**: Excellent performance

### Common Issues

**Low success rate?**
- Train longer (`--timesteps 200000`)
- Check map difficulty
- Watch visually to debug behavior

**Agent gets stuck?**
- May need more training
- Try different reward shaping
- Check sonar readings visually

---

## Quick Reference

| Task | Command |
|------|---------|
| Train model | `python rl/train_rl.py --mode sb3 --timesteps 50000` |
| Test headless | `python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 100` |
| Test visual | `python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --episodes 10` |
| Random baseline | `python rl/test_random_policy.py --episodes 50` |

---

## Full Documentation

- [rl/README.md](rl/README.md) - Detailed examples guide
- [RL_GUIDE.md](rl/RL_GUIDE.md) - Complete RL training guide
- [RL_QUICKREF.md](RL_QUICKREF.md) - Quick reference card

Enjoy testing your trained agents! 🤖
