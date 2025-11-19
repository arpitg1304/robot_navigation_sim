# RL Training Guide

This guide explains how to use the Gymnasium-compatible RL environment for training navigation agents.

## Quick Start

### 1. Install Dependencies

```bash
# Core RL environment
pip install gymnasium>=0.29.0

# Optional: For training with Stable-Baselines3
pip install stable-baselines3>=2.0.0
```

### 2. Run Random Agent Baseline

```bash
python rl/train_rl.py --mode random --episodes 10
```

### 3. Train with PPO (Stable-Baselines3)

```bash
python rl/train_rl.py --mode sb3 --timesteps 50000
```

---

## Environment API

### Creating an Environment

```python
from src.gym_env import ReactiveNavEnv

# Discrete actions (default): turn_left, go_straight, turn_right
env = ReactiveNavEnv(
    map_name="custom_map",
    max_steps=500,
    action_type="discrete"
)

# Continuous actions: [linear_vel, angular_vel]
env = ReactiveNavEnv(
    map_name="custom_map",
    max_steps=500,
    action_type="continuous",
    linear_vel_range=(0.0, 20.0),      # pixels/step
    angular_vel_range=(-45.0, 45.0)    # degrees/step
)
```

### Observation Space

**14-dimensional vector:**

1. **Sonar readings (8 values)**: Normalized distances `[0, 1]` in 8 directions
   - `1.0` = clear path (max range)
   - `0.0` = obstacle immediately adjacent
   - Directions: [0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°]

2. **Goal vector (2 values)**: Normalized `[dx, dy]` to target
   - Unit vector pointing toward goal

3. **Robot heading (2 values)**: `[cos(θ), sin(θ)]`
   - Continuous representation avoiding angle wrapping issues

4. **Linear velocity (1 value)**: Normalized to `[0, 1]`

5. **Angular velocity (1 value)**: Normalized to `[-1, 1]`

### Action Space

#### Discrete (3 actions):
- `0`: Turn left (angular_vel = +45°, half linear speed)
- `1`: Go straight (angular_vel = 0°, full linear speed)
- `2`: Turn right (angular_vel = -45°, half linear speed)

#### Continuous (2D vector):
- `[linear_vel, angular_vel]` both in `[-1, 1]`
- Automatically denormalized to configured velocity ranges

### Reward Function

| Event | Reward | Notes |
|-------|--------|-------|
| **Goal reached** | `+1.0` | Episode terminates |
| **Collision** | `-1.0` | Episode terminates |
| **Distance progress** | `+Δd/100` | Positive when moving toward goal |
| **Step penalty** | `-0.01` | Encourages efficiency |

**Total reward per step:**
```python
if collision:
    reward = -1.0
elif goal_reached:
    reward = +1.0
else:
    reward = (prev_distance - current_distance) / 100.0 - 0.01
```

---

## Usage Examples

### Basic Loop

```python
from src.gym_env import ReactiveNavEnv

env = ReactiveNavEnv(map_name="custom_map")

# Reset environment
obs, info = env.reset()

# Run episode
done = False
total_reward = 0

while not done:
    # Random action
    action = env.action_space.sample()

    # Step
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    done = terminated or truncated

print(f"Episode finished: reward={total_reward}, steps={info['step']}")
env.close()
```

### Training with Stable-Baselines3

```python
from stable_baselines3 import PPO
from src.gym_env import ReactiveNavEnv

# Create environment
env = ReactiveNavEnv(
    map_name="custom_map",
    action_type="discrete"
)

# Create PPO agent
model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
)

# Train
model.learn(total_timesteps=100000)

# Save
model.save("ppo_navigation")

# Evaluate
obs, _ = env.reset()
for _ in range(1000):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, _ = env.reset()

env.close()
```

### Custom Training Loop

```python
import numpy as np
from src.gym_env import ReactiveNavEnv

env = ReactiveNavEnv(map_name="mines", action_type="discrete")

# Simple Q-learning (example)
num_episodes = 1000

for episode in range(num_episodes):
    obs, info = env.reset()
    episode_reward = 0
    done = False

    while not done:
        # Your policy here
        action = your_policy(obs)

        # Step
        next_obs, reward, terminated, truncated, info = env.step(action)
        episode_reward += reward
        done = terminated or truncated

        # Update your policy
        your_policy.update(obs, action, reward, next_obs, done)

        obs = next_obs

    print(f"Episode {episode}: reward={episode_reward:.2f}")

env.close()
```

---

## Available Maps

The environment supports any map in the `maps/` directory:

- `custom_map`: Basic navigation with scattered obstacles
- `mines`: Dense obstacle field
- `passage`: Narrow corridor navigation

List available maps:
```python
from src.environment import Environment
maps = Environment.get_available_maps()
print(maps)
```

---

## Customizing Rewards

You can subclass `ReactiveNavEnv` to implement custom reward functions:

```python
from src.gym_env import ReactiveNavEnv

class CustomRewardEnv(ReactiveNavEnv):
    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)

        # Custom reward shaping
        if not terminated:
            # Reward for moving forward
            if self.robot_linear_vel > 10.0:
                reward += 0.05

            # Penalty for being too close to obstacles
            min_sonar = min(obs[:8])
            if min_sonar < 0.3:
                reward -= 0.1

        return obs, reward, terminated, truncated, info

env = CustomRewardEnv(map_name="custom_map")
```

---

## Performance Tips

### Training Speed
1. **Disable rendering** during training (default):
   ```python
   env = ReactiveNavEnv(render_mode=None)  # Fast
   ```

2. **Use vectorized environments** (SB3):
   ```python
   from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

   # Parallel environments for faster training
   env = SubprocVecEnv([
       lambda: ReactiveNavEnv(map_name="custom_map")
       for _ in range(4)
   ])
   ```

3. **Adjust episode length**:
   ```python
   # Shorter episodes for faster iterations
   env = ReactiveNavEnv(max_steps=200)
   ```

### Hyperparameter Tuning

**For PPO (discrete actions):**
```python
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,       # Try: 1e-4 to 1e-3
    n_steps=2048,             # Try: 1024 to 4096
    batch_size=64,            # Try: 32 to 128
    n_epochs=10,              # Try: 5 to 20
    gamma=0.99,               # Discount factor
    gae_lambda=0.95,          # GAE parameter
    clip_range=0.2,           # PPO clipping
    ent_coef=0.01,            # Entropy bonus (exploration)
)
```

**For SAC (continuous actions):**
```python
from stable_baselines3 import SAC

env = ReactiveNavEnv(action_type="continuous")

model = SAC(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    buffer_size=100000,
    learning_starts=1000,
    batch_size=256,
    tau=0.005,
    gamma=0.99,
)
```

---

## Benchmarking

### Evaluate Agent Performance

```python
from src.gym_env import ReactiveNavEnv

def evaluate(env, model, num_episodes=100):
    """Evaluate agent over multiple episodes."""
    successes = 0
    total_steps = []
    total_rewards = []

    for _ in range(num_episodes):
        obs, _ = env.reset()
        done = False
        episode_reward = 0
        steps = 0

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated

            if terminated and info.get("goal_reached", False):
                successes += 1

        total_steps.append(steps)
        total_rewards.append(episode_reward)

    return {
        "success_rate": successes / num_episodes,
        "avg_steps": np.mean(total_steps),
        "avg_reward": np.mean(total_rewards),
    }

# Usage
env = ReactiveNavEnv(map_name="custom_map")
model = PPO.load("ppo_navigation")
results = evaluate(env, model, num_episodes=100)
print(results)
```

---

## Troubleshooting

### Import Errors
```bash
# Ensure you're running from project root
cd /path/to/reactive-nav-sim-modern
python rl/train_rl.py

# Or install as package
pip install -e .
```

### Low Success Rate
- Increase training timesteps (`--timesteps 200000`)
- Adjust reward shaping (reduce step penalty)
- Try different maps (start with `custom_map`)
- Increase exploration (`ent_coef` for PPO)

### Training Too Slow
- Disable rendering (`render_mode=None`)
- Use parallel environments (`SubprocVecEnv`)
- Reduce `max_steps` per episode
- Use faster algorithm (DQN vs PPO)

---

## Integration with Other RL Libraries

### Gymnasium (Native)
```python
from src.gym_env import ReactiveNavEnv
env = ReactiveNavEnv()  # Already Gymnasium-compatible!
```

### Ray RLlib
```python
from ray.rllib.algorithms.ppo import PPOConfig
from src.gym_env import ReactiveNavEnv

config = (
    PPOConfig()
    .environment(ReactiveNavEnv, env_config={"map_name": "custom_map"})
    .training(lr=3e-4, train_batch_size=2048)
)

algo = config.build()
algo.train()
```

### CleanRL
```python
# ReactiveNavEnv works with any Gymnasium-compatible framework
import gymnasium as gym
from src.gym_env import ReactiveNavEnv

env = ReactiveNavEnv(map_name="custom_map")
# Use with CleanRL implementations directly
```

---

## Next Steps

1. **Experiment with different maps**: Create custom maps using `tools/map_editor.py`
2. **Try continuous actions**: Compare discrete vs continuous action spaces
3. **Implement curriculum learning**: Start with easy maps, progress to harder ones
4. **Add visual observations**: Extend observation space with pixel data
5. **Multi-agent navigation**: Extend for cooperative/competitive scenarios

For more examples, see `rl/train_rl.py`!
