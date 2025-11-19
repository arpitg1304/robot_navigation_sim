"""Test environment with random policy (no trained model needed).

This script is useful for:
- Testing the environment setup
- Establishing a baseline performance
- Debugging rendering issues

Usage:
    # Headless mode
    python rl/test_random_policy.py --episodes 50

    # With visualization
    python rl/test_random_policy.py --episodes 10 --render
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gym_env import ReactiveNavEnv


def test_random_policy(
    env, num_episodes=10, render=False, fps=30, verbose=True
):
    """
    Test environment with random actions.

    Args:
        env: Environment instance
        num_episodes: Number of episodes to run
        render: Whether to render visualization
        fps: Target FPS for rendering
        verbose: Print per-episode results

    Returns:
        dict: Statistics
    """
    frame_time = 1.0 / fps if render else 0

    successes = 0
    collisions = 0
    timeouts = 0
    episode_rewards = []
    episode_lengths = []
    final_distances = []

    print("\n" + "=" * 70)
    print("RANDOM POLICY TEST")
    print("=" * 70)
    print(f"Episodes: {num_episodes}")
    print(f"Render: {render}")
    if render:
        print(f"FPS: {fps}")
    print("=" * 70 + "\n")

    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        done = False

        while not done:
            start_time = time.time()

            # Random action
            action = env.action_space.sample()

            # Step
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated

            # Render if requested
            if render:
                env.render()

                # Maintain FPS
                elapsed = time.time() - start_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

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

        if render:
            time.sleep(0.5)  # Brief pause between episodes

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
    }

    return stats


def print_statistics(stats):
    """Pretty print statistics."""
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Episodes:              {stats['num_episodes']}")
    print()
    print("OUTCOMES:")
    print(f"  Success Rate:        {stats['success_rate']:6.1%}")
    print(f"  Collision Rate:      {stats['collision_rate']:6.1%}")
    print(f"  Timeout Rate:        {stats['timeout_rate']:6.1%}")
    print()
    print("PERFORMANCE:")
    print(f"  Average Reward:      {stats['avg_reward']:7.2f} ± {stats['std_reward']:.2f}")
    print(f"  Average Steps:       {stats['avg_steps']:7.1f} ± {stats['std_steps']:.1f}")
    print(f"  Avg Final Distance:  {stats['avg_final_distance']:7.1f}")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test environment with random policy"
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=10,
        help="Number of episodes (default: 10)",
    )
    parser.add_argument(
        "--map",
        type=str,
        default="custom_map",
        help="Map to use (default: custom_map)",
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
        "--render",
        action="store_true",
        help="Enable visualization (slower)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Target FPS for rendering (default: 30)",
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

    # Create environment
    print(f"Creating environment...")
    print(f"  Map: {args.map}")
    print(f"  Action type: {args.action_type}")
    print(f"  Max steps: {args.max_steps}")

    env = ReactiveNavEnv(
        map_name=args.map,
        max_steps=args.max_steps,
        action_type=args.action_type,
        render_mode="human" if args.render else None,
    )

    if args.seed is not None:
        print(f"  Seed: {args.seed}")
        env.reset(seed=args.seed)

    # Run test
    try:
        stats = test_random_policy(
            env=env,
            num_episodes=args.episodes,
            render=args.render,
            fps=args.fps,
            verbose=not args.quiet,
        )

        # Print results
        print_statistics(stats)

    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        env.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
