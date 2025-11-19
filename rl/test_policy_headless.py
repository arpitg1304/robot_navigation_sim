"""Test a trained RL policy without visualization (headless mode).

This script evaluates a trained model across multiple episodes and reports statistics.
Usage:
    python rl/test_policy_headless.py --model models/ppo_reactive_nav.zip --episodes 100
"""

import argparse
import sys
from pathlib import Path

import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gym_env import ReactiveNavEnv


def evaluate_policy(model, env, num_episodes=100, deterministic=True, verbose=True):
    """
    Evaluate a trained policy over multiple episodes.

    Args:
        model: Trained model with .predict() method
        env: Environment instance
        num_episodes: Number of episodes to evaluate
        deterministic: Use deterministic actions (no exploration)
        verbose: Print per-episode results

    Returns:
        dict: Statistics including success rate, avg reward, avg steps
    """
    successes = 0
    collisions = 0
    timeouts = 0
    episode_rewards = []
    episode_lengths = []
    final_distances = []

    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=deterministic)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated

        # Track outcomes
        episode_rewards.append(episode_reward)
        episode_lengths.append(steps)
        final_distances.append(info["distance_to_goal"])

        if terminated:
            if info.get("goal_reached", False):
                successes += 1
                outcome = "SUCCESS ✓"
            else:
                collisions += 1
                outcome = "COLLISION ✗"
        else:
            timeouts += 1
            outcome = "TIMEOUT ⏱"

        if verbose:
            print(
                f"Episode {episode + 1:3d}/{num_episodes}: {outcome:12s} | "
                f"Reward: {episode_reward:7.2f} | Steps: {steps:3d} | "
                f"Distance: {info['distance_to_goal']:6.1f}"
            )

    # Calculate statistics
    stats = {
        "num_episodes": num_episodes,
        "success_rate": successes / num_episodes,
        "collision_rate": collisions / num_episodes,
        "timeout_rate": timeouts / num_episodes,
        "avg_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "avg_steps": np.mean(episode_lengths),
        "std_steps": np.std(episode_lengths),
        "avg_final_distance": np.mean(final_distances),
        "min_steps": np.min(episode_lengths),
        "max_steps": np.max(episode_lengths),
    }

    return stats


def print_statistics(stats):
    """Pretty print evaluation statistics."""
    print("\n" + "=" * 70)
    print("EVALUATION STATISTICS")
    print("=" * 70)
    print(f"Episodes:              {stats['num_episodes']}")
    print()
    print("OUTCOMES:")
    print(f"  Success Rate:        {stats['success_rate']:6.1%}  ({int(stats['success_rate'] * stats['num_episodes'])}/{stats['num_episodes']})")
    print(f"  Collision Rate:      {stats['collision_rate']:6.1%}  ({int(stats['collision_rate'] * stats['num_episodes'])}/{stats['num_episodes']})")
    print(f"  Timeout Rate:        {stats['timeout_rate']:6.1%}  ({int(stats['timeout_rate'] * stats['num_episodes'])}/{stats['num_episodes']})")
    print()
    print("PERFORMANCE:")
    print(f"  Average Reward:      {stats['avg_reward']:7.2f} ± {stats['std_reward']:.2f}")
    print(f"  Average Steps:       {stats['avg_steps']:7.1f} ± {stats['std_steps']:.1f}")
    print(f"  Steps Range:         [{stats['min_steps']}, {stats['max_steps']}]")
    print(f"  Avg Final Distance:  {stats['avg_final_distance']:7.1f}")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate trained RL policy (headless mode)"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to trained model (e.g., models/ppo_reactive_nav.zip)",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=100,
        help="Number of evaluation episodes (default: 100)",
    )
    parser.add_argument(
        "--map",
        type=str,
        default="custom_map",
        help="Map to evaluate on (default: custom_map)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=500,
        help="Maximum steps per episode (default: 500)",
    )
    parser.add_argument(
        "--action-type",
        type=str,
        default="discrete",
        choices=["discrete", "continuous"],
        help="Action space type (default: discrete)",
    )
    parser.add_argument(
        "--stochastic",
        action="store_true",
        help="Use stochastic policy (exploration)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Don't print per-episode results",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )

    args = parser.parse_args()

    # Check if model exists
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        print("\nTrain a model first:")
        print("  python rl/train_rl.py --mode sb3 --timesteps 50000")
        return 1

    # Load model
    print(f"Loading model from {model_path}...")
    try:
        from stable_baselines3 import PPO

        model = PPO.load(str(model_path))
        print("✓ Model loaded successfully")
    except ImportError:
        print("Error: stable-baselines3 not installed")
        print("Install with: pip install stable-baselines3")
        return 1
    except Exception as e:
        print(f"Error loading model: {e}")
        return 1

    # Create environment
    print(f"\nCreating environment...")
    print(f"  Map: {args.map}")
    print(f"  Action type: {args.action_type}")
    print(f"  Max steps: {args.max_steps}")

    env = ReactiveNavEnv(
        map_name=args.map,
        max_steps=args.max_steps,
        action_type=args.action_type,
        render_mode=None,  # Headless
    )

    if args.seed is not None:
        print(f"  Seed: {args.seed}")
        env.reset(seed=args.seed)

    # Evaluate
    print(f"\nEvaluating for {args.episodes} episodes...")
    print()

    stats = evaluate_policy(
        model=model,
        env=env,
        num_episodes=args.episodes,
        deterministic=not args.stochastic,
        verbose=not args.quiet,
    )

    # Print results
    print_statistics(stats)

    env.close()

    # Return success code based on performance
    if stats["success_rate"] > 0.5:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
