# Multi-Map Training in TUI

The TUI now supports **multi-map training** for better generalization!

## 🎯 Quick Start

```bash
python rl_tui.py
```

1. Select **Train**
2. Choose **"Multi-Map"** (option 2)
3. Select which maps to train on
4. Follow the prompts
5. Get a model that works across maps!

## 🌟 Training Options

### Option 1: Single Map (Old Way)
- Trains on one map only
- **Pros:** Higher success rate on that map (60-90%)
- **Cons:** Doesn't work on other maps (0-10%)
- **Use for:** Benchmarking, competitions on specific map

### Option 2: Multi-Map (New! Recommended)
- Trains on multiple maps
- **Pros:** Works across all maps (40-60%)
- **Cons:** Lower success on individual maps
- **Use for:** General navigation, real-world applications

## 📋 Multi-Map Selection

When you choose multi-map training, you'll see:

```
Select Maps for Multi-Map Training:
  1. All maps (best generalization)
  2. All except challenge (easier training)
  3. Custom selection
```

**Recommendations:**

| Goal | Choose | Why |
|------|--------|-----|
| **Best generalization** | All maps | Tests diverse scenarios |
| **Faster training** | All except challenge | Challenge is very hard |
| **Specific use case** | Custom | Pick relevant maps |

## 🎮 Example Session

```
Training Type:
  1. Single Map
  2. Multi-Map ← Choose this!

Select maps [1/2/3] (1): 1
✓ Selected maps: challenge, custom_map, mines, passage

Action Type:
  1. Discrete

Select action type: 1
✓ Action type: discrete

Training Duration:
  1. Quick test (10k steps)
  2. Short (50k steps)
  3. Medium (100k steps)
  4. Long (200k steps) ← Recommended for multi-map

Select duration: 4
✓ Timesteps: 200,000

Model name [ppo_multimap_discrete.zip]:

Training Configuration:
  Maps: challenge, custom_map, mines, passage
  Mode: Multi-Map (generalizes)
  Action Type: discrete
  Timesteps: 200,000

Start training? [Y/n]: y

[Training progress bar...]

✓ Training complete!
Model saved to: models/ppo_multimap_discrete.zip

This model trained on multiple maps!
✓ Should generalize across different maps

Test it on each map:
  • challenge
  • custom_map
  • mines
  • passage
```

## 🧪 Testing Multi-Map Models

After training, test on each map:

**From TUI:**
1. Select **Test**
2. Choose your multi-map model
3. Test on each map individually

**From Command Line:**
```bash
model="models/ppo_multimap_discrete.zip"

for map in challenge custom_map mines passage; do
    echo "Testing on $map..."
    python rl/test_policy_headless.py \
        --model $model \
        --map $map \
        --episodes 50 \
        --quiet
done
```

## 📊 Expected Results

### Single-Map Training
| Map | Success on Training Map | Success on Other Maps |
|-----|-------------------------|----------------------|
| custom_map | 70-90% | 0-20% |
| challenge | 60-80% | 0-10% |

### Multi-Map Training
| Map | Success Rate |
|-----|-------------|
| custom_map | 50-70% |
| mines | 40-60% |
| passage | 30-50% |
| challenge | 10-30% |

**Trade-off:** Lower peak performance, but works everywhere!

## 💡 Tips

1. **Use more timesteps for multi-map**
   - Single map: 50k-100k sufficient
   - Multi-map: 150k-200k recommended

2. **Start with easier maps**
   - "All except challenge" for first training
   - Add challenge later when you have experience

3. **Compare approaches**
   - Train one single-map model
   - Train one multi-map model
   - See which works better for your use case

4. **Visual testing helps**
   - Use visual mode to see where it fails
   - Helps understand what the agent learned

## 🔧 How It Works

Under the hood, multi-map training:
1. Randomly picks a map at the start of each episode
2. Robot navigates that map
3. Next episode: different random map
4. Repeat for all timesteps

This forces the agent to learn **general navigation skills** instead of memorizing specific paths.

## 🚀 Quick Commands Comparison

**Single-Map:**
```bash
python rl_tui.py
→ Train → Single Map → custom_map → ...
```

**Multi-Map:**
```bash
python rl_tui.py
→ Train → Multi-Map → All maps → ...
```

**Command Line (if you prefer):**
```bash
python rl/train_multi_map.py --timesteps 200000
```

## ❓ FAQ

**Q: Why does my single-map model fail on other maps?**
A: It memorized obstacle positions instead of learning general navigation. Use multi-map training!

**Q: Should I always use multi-map?**
A: Use multi-map for generalization, single-map if you only care about one specific map.

**Q: How much longer does multi-map training take?**
A: About 2-4x more timesteps needed (use 150k-200k instead of 50k).

**Q: Can I add my own maps to multi-map training?**
A: Yes! Just create maps in `maps/` folder and they'll appear in the selection.

---

Happy training! 🎉
