# Fixing Overfitting - Training for Generalization

## 🔴 Problem: Model Only Works on Training Map

**Symptoms:**
- Agent navigates well on map it was trained on
- Agent spins in circles or fails immediately on other maps
- No transfer of learned skills

**Cause:** **Overfitting** - The model memorized specific obstacle positions instead of learning general navigation.

---

## ✅ Solution 1: Train on Multiple Maps

Train a single policy that sees different maps each episode:

```bash
# Train on all maps
python rl/train_multi_map.py --timesteps 200000

# Train on specific maps
python rl/train_multi_map.py --maps custom_map mines passage --timesteps 150000
```

**How it works:**
- Each episode randomly selects a different map
- Forces agent to learn general skills (avoid obstacles, reach goal)
- Cannot memorize specific paths

**Expected results:**
- 30-50% success across ALL maps
- Better than single-map training (60%+) on one map but generalizes

---

## ✅ Solution 2: Curriculum Learning

Train progressively on harder maps:

```bash
# Step 1: Learn basics (50k steps)
python rl/train_rl.py --mode sb3 --map custom_map --timesteps 50000
mv models/ppo_reactive_nav.zip models/stage1.zip

# Step 2: Add complexity (50k steps, start from stage1)
python rl/train_rl.py --mode sb3 --map mines --timesteps 50000
# (Load stage1 weights first in code)

# Step 3: Advanced (50k steps)
python rl/train_rl.py --mode sb3 --map challenge --timesteps 50000
```

---

## ✅ Solution 3: Domain Randomization

Modify `src/gym_env.py` to add randomness:

```python
def reset(self, seed=None, options=None):
    # ... existing code ...

    # Add noise to start position
    self.robot_x += np.random.uniform(-20, 20)
    self.robot_y += np.random.uniform(-20, 20)

    # Randomly rotate map (advanced)
    # ...

    return observation, info
```

---

## ✅ Solution 4: Use Relative Observations

The current observation includes:
- Sonar readings (✓ relative to robot)
- Goal vector (✓ relative to robot)
- Heading (✓ relative)
- Velocities (✓ relative)

**Already good!** The observations are relative, so overfitting is likely due to:
1. Not enough diverse training
2. Map-specific exploitation

---

## 🎯 Recommended Approach

### For Best Generalization:

**Option A: Multi-Map Training (Easiest)**
```bash
# Train on all maps except challenge (easier learning)
python rl/train_multi_map.py \
    --maps custom_map mines passage \
    --timesteps 200000 \
    --model-name ppo_generalizer.zip

# Test on all maps
for map in custom_map mines passage challenge; do
    python rl/test_policy_headless.py \
        --model models/ppo_generalizer.zip \
        --map $map \
        --episodes 50 \
        --quiet
done
```

**Expected Results:**
- custom_map: 50-70% success
- mines: 40-60% success
- passage: 30-50% success
- challenge: 10-30% success (hardest)

**Option B: Per-Map Specialists**
```bash
# Train separate models for each map
for map in custom_map mines passage challenge; do
    python rl/train_rl.py \
        --mode sb3 \
        --map $map \
        --timesteps 100000

    mv models/ppo_reactive_nav.zip models/ppo_$map.zip
done
```

**Expected Results:**
- Each model: 60-90% on its own map
- Each model: 0-20% on other maps

---

## 📊 Comparison

| Approach | Training Time | Single Map | All Maps | Best For |
|----------|---------------|------------|----------|----------|
| **Single Map** | Fast (50k) | 60-90% | 0-20% | Benchmarking one map |
| **Multi-Map** | Medium (200k) | 40-60% | 40-60% | **General navigation** |
| **Curriculum** | Slow (150k+) | 50-70% | 30-50% | Research |
| **Specialist** | Per map (100k) | 70-90% | 0-20% | Production use |

---

## 🧪 Testing Generalization

After training, test on ALL maps:

```bash
# Quick test script
model="models/ppo_multi_map.zip"

for map in custom_map mines passage challenge; do
    echo "Testing on $map..."
    python rl/test_policy_headless.py \
        --model $model \
        --map $map \
        --episodes 100 \
        --quiet
    echo ""
done
```

---

## 💡 Why Your Current Model Fails

Your model trained on "challenge" learned:
- "At position (X, Y), turn left"
- "Obstacle at (A, B), go right"
- Specific waypoints for challenge map

On other maps:
- Those positions don't exist
- Learned patterns don't apply
- Agent is confused → spins in place

**Solution:** Train on multiple maps so it learns:
- "When sonar detects obstacle ahead, turn"
- "When goal is left, steer left"
- General policies, not specific paths

---

## 🚀 Quick Fix (5 min)

```bash
# Train on all easy maps
python rl/train_multi_map.py --maps custom_map mines passage --timesteps 100000

# Test it
python rl/test_policy_visual.py --model models/ppo_multi_map.zip --map custom_map
python rl/test_policy_visual.py --model models/ppo_multi_map.zip --map mines
```

This should give you a policy that works reasonably well on multiple maps!

---

## 📚 Further Reading

- [Domain Randomization](https://arxiv.org/abs/1703.06907)
- [Curriculum Learning](https://arxiv.org/abs/1904.04475)
- [Generalization in Deep RL](https://arxiv.org/abs/1810.12894)
