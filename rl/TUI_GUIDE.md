# Terminal UI Guide

A simple, interactive terminal interface for training and testing RL navigation agents.

## Quick Start

```bash
python rl_tui.py
```

That's it! The TUI will guide you through everything.

## Features

### 🎯 Main Menu

When you launch the TUI, you'll see:

1. **Available Models** - Automatically lists all trained models in `models/` directory
2. **Main Menu** with 4 options:
   - Train - Train a new RL agent
   - Test - Test a trained agent
   - Baseline - Run random baseline
   - Quit - Exit the TUI

### 🏋️ Training Mode

**Step-by-step training workflow:**

1. **Select Map**
   - Choose from: `custom_map`, `mines`, `passage`
   - Uses interactive numbered menu

2. **Select Action Type**
   - Discrete: 3 actions (turn_left, go_straight, turn_right)
   - Continuous: 2D vector (linear_vel, angular_vel)

3. **Select Training Duration**
   - Quick test: 10k steps (~1 min)
   - Short: 50k steps (~3 min)
   - Medium: 100k steps (~5 min)
   - Long: 200k steps (~10 min)
   - Custom: Enter your own

4. **Name Your Model**
   - Default: `ppo_{map}_{action_type}.zip`
   - Or provide custom name

5. **Confirm and Train**
   - Review configuration
   - Confirm to start training
   - Watch progress bar
   - Model automatically saved to `models/` directory

### 🧪 Testing Mode

**Step-by-step testing workflow:**

1. **Select Model**
   - Choose from available models
   - Shows model size for reference

2. **Select Map**
   - Test on same map as training
   - Or test generalization on different map

3. **Select Test Mode**
   - Headless: Fast, comprehensive statistics
   - Visual: Watch agent navigate in real-time

4. **Set Episodes**
   - Default: 10 for visual, 100 for headless
   - Or enter custom amount

5. **View Results**
   - Per-episode results shown live
   - Final statistics panel with:
     - Success rate
     - Collision rate
     - Timeout rate
     - Average reward
     - Average steps

### 📊 Random Baseline Mode

**Quick baseline testing:**

1. **Select Map**
2. **Choose Visualization** (optional)
3. **Set Episodes**
4. **View Results**

Shows how a random policy performs - useful for:
- Establishing baseline performance
- Verifying environment works
- Comparing against trained agents

## Example Session

### Training a Model

```
Main Menu:
  1. Train
  2. Test
  3. Baseline
  4. Quit

Select option: 1

Available Maps:
  1. custom_map
  2. mines
  3. passage

Select map: 2
✓ Selected map: mines

Action Type:
  1. Discrete
  2. Continuous

Select action type: 1
✓ Action type: discrete

Training Duration:
  1. Quick test (10k steps, ~1 min)
  2. Short (50k steps, ~3 min)
  3. Medium (100k steps, ~5 min)
  4. Long (200k steps, ~10 min)
  5. Custom

Select duration: 3
✓ Timesteps: 100,000

Model name [ppo_mines_discrete.zip]:

Training Configuration:
  Map: mines
  Action Type: discrete
  Timesteps: 100,000
  Model: ppo_mines_discrete.zip

Start training? [Y/n]: y

[Progress bar shows training...]

✓ Training complete!
Model saved to: models/ppo_mines_discrete.zip
```

### Testing a Model

```
Available Models
┌───┬─────────────────────────┬──────────┐
│ # │ Model Name              │     Size │
├───┼─────────────────────────┼──────────┤
│ 1 │ ppo_mines_discrete.zip  │ 154.5 KB │
│ 2 │ ppo_reactive_nav.zip    │ 154.4 KB │
└───┴─────────────────────────┴──────────┘

Select model: 1
✓ Selected model: ppo_mines_discrete.zip

Available Maps:
  1. custom_map
  2. mines
  3. passage

Select map: 2
✓ Selected map: mines

Test Mode:
  1. Headless (fast, comprehensive stats)
  2. Visual (watch the agent navigate)

Select mode: 1

Number of episodes [100]:

Running 100 episodes...

Episode   1/100: SUCCESS ✓  | Reward:    0.85 | Steps:  45
Episode   2/100: COLLISION ✗ | Reward:   -1.20 | Steps:  88
...

╭──────────────────────────────╮
│ Test Results                 │
│                              │
│ Success Rate:   45.0% (45/100)│
│ Collision Rate: 30.0% (30/100)│
│ Timeout Rate:  25.0% (25/100) │
│                              │
│ Avg Reward:    -0.85 ± 2.14  │
│ Avg Steps:    156.3 ± 145.2  │
╰──────────────────────────────╯
```

## Tips

### 🎯 Best Practices

1. **Start with Baseline**
   - Run random baseline first to see baseline performance (~0-5% success)

2. **Train on Specific Maps**
   - Train separate models for each map for best performance
   - Name them clearly: `ppo_mines_discrete.zip`

3. **Test Generalization**
   - Train on one map, test on others
   - See how well policies generalize

4. **Use Visual Testing**
   - Watch agent behavior to debug issues
   - Understand what the agent learned

5. **Compare Models**
   - Train with different action types
   - Train with different timesteps
   - Test all on same map to compare

### ⚡ Performance Expectations

| Training | Expected Success | Time |
|----------|-----------------|------|
| Random   | 0-5%           | N/A  |
| 10k steps| 10-20%         | ~1m  |
| 50k steps| 30-50%         | ~3m  |
| 100k steps| 50-70%        | ~5m  |
| 200k steps| 70-90%        | ~10m |

## Keyboard Controls

- **Ctrl+C**: Cancel current operation and return to menu
- **Enter**: Accept default choice or continue

## Troubleshooting

### "stable-baselines3 not installed"
```bash
pip install stable-baselines3
```

### "No models found"
Train a model first using option 1 (Train).

### "pygame error" during visual testing
```bash
pip install pygame
```

### Model performs poorly
- Train longer (increase timesteps)
- Check you're testing on the right map
- Use visual mode to see what's happening

## Advanced Usage

### Save Training Logs

The TUI uses Stable-Baselines3 with `verbose=1`, so training logs are shown in the terminal. To save them:

```bash
python rl_tui.py 2>&1 | tee training.log
```

### Custom Configurations

For more control over hyperparameters, use the command-line scripts in `rl/` directory instead of the TUI.

## What the TUI Does

Under the hood, the TUI:
- Scans `models/` directory for `.zip` files
- Creates ReactiveNavEnv with selected configuration
- Uses Stable-Baselines3 PPO for training
- Saves models with descriptive names
- Provides formatted statistics and progress

It's essentially a user-friendly wrapper around the command-line scripts!

## Comparison: TUI vs Command Line

| Feature | TUI | Command Line |
|---------|-----|--------------|
| Easy to use | ✅ Yes | ❌ Need to know args |
| Model discovery | ✅ Automatic | ❌ Manual |
| Interactive | ✅ Yes | ❌ No |
| Scriptable | ❌ No | ✅ Yes |
| Custom hyperparams | ❌ No | ✅ Yes |
| Ideal for | Beginners, Quick tests | Automation, Advanced |

**Use TUI for:** Interactive exploration, quick tests, learning
**Use CLI for:** Automation, scripts, custom configurations

---

Enjoy the simplified RL training experience! 🚀
