# RL Environment Quick Reference

## 🎯 Interactive TUI (Easiest!)

```bash
python rl_tui.py
```

**Features:**
- ✨ Interactive menus (no command-line args!)
- 📂 Auto-detects trained models
- 🗺️ Map selection dropdowns
- 📊 Real-time training progress
- 🧪 Both training & testing modes

See [TUI_GUIDE.md](rl/TUI_GUIDE.md) for details.

---

## Installation

```bash
pip install gymnasium rich
pip install stable-baselines3  # Optional
```

## Basic Usage (Code)

```python
from src.gym_env import ReactiveNavEnv

# Create environment
env = ReactiveNavEnv(
    map_name="custom_map",       # Map to use
    action_type="discrete",      # "discrete" or "continuous"
    max_steps=500,               # Max steps per episode
)

# Reset
obs, info = env.reset()

# Step
obs, reward, terminated, truncated, info = env.step(action)

# Close
env.close()
```

## Observation Space (14D)

| Index | Description | Range |
|-------|-------------|-------|
| 0-7   | Sonar readings (8 directions) | [0, 1] |
| 8-9   | Goal vector (dx, dy normalized) | [-1, 1] |
| 10-11 | Heading (cos θ, sin θ) | [-1, 1] |
| 12    | Linear velocity | [0, 1] |
| 13    | Angular velocity | [-1, 1] |

## Action Space

### Discrete (default)
- `0`: Turn left
- `1`: Go straight
- `2`: Turn right

### Continuous
- `[linear_vel, angular_vel]` both in `[-1, 1]`

## Rewards

| Event | Reward |
|-------|--------|
| Reach goal | +1.0 |
| Collision | -1.0 |
| Progress toward goal | +Δd/100 |
| Each step | -0.01 |

## Quick Commands

### Using TUI (Recommended)
```bash
# Launch interactive menu
python rl_tui.py

# Then follow prompts to:
# 1. Train - Select map, action type, duration
# 2. Test - Select model, map, visualization
# 3. Baseline - Random policy testing
```

### Command Line

**Random Agent**
```bash
python rl/train_rl.py --mode random --episodes 5
```

**Train PPO**
```bash
python rl/train_rl.py --mode sb3 --timesteps 50000
```

**Test Headless**
```bash
python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 100
```

**Test Visual**
```bash
python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip --episodes 10
```

### Custom Code
```python
from stable_baselines3 import PPO
from src.gym_env import ReactiveNavEnv

env = ReactiveNavEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=50000)
model.save("my_agent")
```

## Available Maps
- `custom_map` - Basic navigation
- `mines` - Dense obstacles
- `passage` - Narrow corridors

## Command Line Options

```bash
python rl/train_rl.py \
  --mode random|sb3 \
  --action-type discrete|continuous \
  --map custom_map \
  --episodes 10 \
  --timesteps 50000 \
  --max-steps 500 \
  --render  # Show visualization (slow)
```

## Common Patterns

### Evaluate trained model
```python
model = PPO.load("my_agent")
obs, _ = env.reset()

for _ in range(100):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, term, trunc, info = env.step(action)
    if term or trunc:
        print(f"Goal: {info['goal_reached']}, Steps: {info['step']}")
        obs, _ = env.reset()
```

### Custom reward function
```python
class MyEnv(ReactiveNavEnv):
    def step(self, action):
        obs, reward, term, trunc, info = super().step(action)
        # Add custom reward shaping here
        return obs, reward, term, trunc, info
```

### Vectorized training
```python
from stable_baselines3.common.vec_env import SubprocVecEnv

env = SubprocVecEnv([
    lambda: ReactiveNavEnv() for _ in range(4)
])
model = PPO("MlpPolicy", env)
model.learn(total_timesteps=200000)
```

## Performance Tips

1. **Disable rendering**: `render_mode=None` (default)
2. **Use vectorized envs**: 4-8 parallel environments
3. **Reduce max_steps**: Start with 200-300
4. **Tune exploration**: Adjust `ent_coef` in PPO

## Workflow Comparison

| Task | TUI | Command Line |
|------|-----|--------------|
| **Train model** | Menu → Train → Select options → Start | `python rl/train_rl.py --mode sb3 --timesteps 50000` |
| **Test model** | Menu → Test → Select model/map → View | `python rl/test_policy_headless.py --model X --episodes 100` |
| **Visual test** | Menu → Test → Visual mode → Watch | `python rl/test_policy_visual.py --model X --episodes 10` |
| **Baseline** | Menu → Baseline → Select options | `python rl/test_random_policy.py --episodes 50` |

**TUI = Easy & Interactive** | **CLI = Automation & Scripting**

## Documentation

- TUI Guide: [TUI_GUIDE.md](rl/TUI_GUIDE.md)
- Full guide: [RL_GUIDE.md](rl/RL_GUIDE.md)
- Test guide: [TEST_POLICIES.md](rl/TEST_POLICIES.md)
- Main README: [README.md](README.md)
