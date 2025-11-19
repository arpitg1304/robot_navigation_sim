# Challenge Map

An advanced navigation challenge designed to test sophisticated path planning and obstacle avoidance.

## 🎯 Objectives

**Start Position:** (150, 550) - Bottom-left
**Goal Position:** (550, 150) - Top-right
**Diagonal Distance:** ~565 pixels
**Difficulty:** ⭐⭐⭐⭐⭐ (Advanced)

## 🗺️ Map Features

### 1. Entrance Corridor
- Narrow passage at the start
- Forces robot into specific path
- Tests initial navigation accuracy

### 2. Central Maze Section
- Horizontal and vertical barriers
- Multiple possible paths
- Requires strategic decision-making

### 3. Obstacle Clusters
- Circular obstacle groups (middle-left)
- Dense formation requiring precision
- Tests local obstacle avoidance

### 4. Narrow Passages
- S-curve path sections
- Tight corridors
- Precision maneuvering required

### 5. Guard Obstacles
- Strategically placed near goal
- Requires careful final approach
- Tests goal-seeking under constraints

### 6. Diverse Shapes
- 27 total obstacles
- Mix of circles, polygons, rectangles, triangles
- Tests generalization across obstacle types

## 📊 Recommended for:

- **RL Training:** Excellent for advanced policy learning
- **Algorithm Testing:** Benchmarks complex navigation
- **Performance Evaluation:** Distinguishes good vs great policies

## 🎮 Usage

### Interactive Simulator
```bash
python -m src.main
# Select "challenge" from map dropdown
```

### RL Training (TUI)
```bash
python rl_tui.py
# Menu → Train → Select "challenge" map
```

### RL Training (CLI)
```bash
python rl/train_rl.py --mode sb3 --map challenge --timesteps 100000
```

### RL Testing
```bash
python rl/test_policy_headless.py --model models/ppo_challenge.zip --map challenge --episodes 100
```

## 🏆 Success Metrics

| Metric | Beginner | Intermediate | Advanced |
|--------|----------|--------------|----------|
| Success Rate | <10% | 10-40% | 40%+ |
| Avg Steps | 400+ | 200-400 | <200 |
| Training Steps | 200k+ | 100-200k | <100k |

## 💡 Training Tips

1. **Train longer:** This map needs 100k-200k steps minimum
2. **Use continuous actions:** Better for tight corridors
3. **Adjust max_steps:** Try 600-800 for this map
4. **Curriculum learning:** Train on easier maps first, then transfer
5. **Visual testing:** Watch failures to understand bottlenecks

## 🧪 Comparison to Other Maps

| Map | Difficulty | Obstacles | Success Rate (50k steps) |
|-----|------------|-----------|--------------------------|
| custom_map | ⭐⭐ | 5 | ~60% |
| mines | ⭐⭐⭐ | 8 | ~40% |
| passage | ⭐⭐⭐⭐ | 6 | ~30% |
| **challenge** | ⭐⭐⭐⭐⭐ | 27 | ~10% |

## 🎨 Map Layout

```
┌────────────────────────────────────────┐
│                        ███  TARGET🎯   │
│  ███  ◆   ██████████   ●               │
│            │           ●               │
│   ●  ●  ●  │  ████████ ●  ◆  ◆        │
│   ● ●      │                           │
│            │      ████                 │
│  ███████████████  ║                    │
│                   ║    ◆               │
│  █     ███████████████ ●               │
│  █                ║                    │
│  █   ●    ███     ║                    │
│          START🤖  ║            ███     │
└────────────────────────────────────────┘

Legend:
  🤖 = Start
  🎯 = Goal
  ● = Circular obstacle
  █ = Rectangular barrier
  ◆ = Diamond/polygon obstacle
  ║ = Narrow corridor
```

## 🔧 Created With

```bash
python tools/create_challenge_map.py
```

This map was procedurally designed with:
- Strategic obstacle placement
- Multiple path options (no single solution)
- Graduated difficulty zones
- Testing various navigation skills

---

**Good luck navigating this challenge!** 🚀
