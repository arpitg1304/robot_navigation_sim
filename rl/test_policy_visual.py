"""Test a trained RL policy with visual rendering.

This script runs a trained model and displays the robot's behavior in the simulator UI.
Usage:
    python rl/test_policy_visual.py --model models/ppo_reactive_nav.zip
"""

import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gym_env import ReactiveNavEnv


def run_visual_episodes(model, env, num_episodes=10, fps=30, deterministic=True):
    """
    Run episodes with visual rendering.

    Args:
        model: Trained model with .predict() method
        env: Environment instance with rendering enabled
        num_episodes: Number of episodes to run
        fps: Target frames per second for rendering
        deterministic: Use deterministic actions
    """
    frame_time = 1.0 / fps

    successes = 0
    total_episodes = 0

    print("\n" + "=" * 70)
    print("VISUAL POLICY TEST")
    print("=" * 70)
    print(f"Episodes: {num_episodes}")
    print(f"FPS: {fps}")
    print(f"Policy: {'Deterministic' if deterministic else 'Stochastic'}")
    print("\nPress Ctrl+C to stop early")
    print("=" * 70 + "\n")

    try:
        for episode in range(num_episodes):
            obs, info = env.reset()
            episode_reward = 0
            steps = 0
            done = False

            print(f"\n--- Episode {episode + 1}/{num_episodes} ---")
            print(f"Starting position: ({info['robot_x']:.1f}, {info['robot_y']:.1f})")
            print(f"Goal distance: {info['distance_to_goal']:.1f}")

            while not done:
                start_time = time.time()

                # Get action from model
                action, _ = model.predict(obs, deterministic=deterministic)

                # Step environment
                obs, reward, terminated, truncated, info = env.step(action)
                episode_reward += reward
                steps += 1
                done = terminated or truncated

                # Render
                env.render()

                # Maintain target FPS
                elapsed = time.time() - start_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

            # Episode finished
            total_episodes += 1

            if terminated and info.get("goal_reached", False):
                successes += 1
                outcome = "✓ SUCCESS!"
                outcome_color = "\033[92m"  # Green
            elif info.get("collision", False):
                outcome = "✗ Collision"
                outcome_color = "\033[91m"  # Red
            else:
                outcome = "⏱ Timeout"
                outcome_color = "\033[93m"  # Yellow

            reset_color = "\033[0m"

            print(
                f"{outcome_color}{outcome}{reset_color} | "
                f"Reward: {episode_reward:6.2f} | "
                f"Steps: {steps:3d} | "
                f"Final distance: {info['distance_to_goal']:.1f}"
            )

            # Brief pause between episodes
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    # Print summary
    if total_episodes > 0:
        success_rate = successes / total_episodes
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Episodes completed: {total_episodes}/{num_episodes}")
        print(f"Success rate: {success_rate:.1%} ({successes}/{total_episodes})")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Visualize trained RL policy in simulator"
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
        default=10,
        help="Number of episodes to visualize (default: 10)",
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
        "--fps",
        type=int,
        default=30,
        help="Target frames per second (default: 30)",
    )
    parser.add_argument(
        "--stochastic",
        action="store_true",
        help="Use stochastic policy instead of deterministic",
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

    # Create environment with rendering
    print(f"\nInitializing simulator...")
    print(f"  Map: {args.map}")
    print(f"  Action type: {args.action_type}")
    print(f"  Max steps: {args.max_steps}")
    print(f"  FPS: {args.fps}")

    try:
        env = ReactiveNavEnv(
            map_name=args.map,
            max_steps=args.max_steps,
            action_type=args.action_type,
            render_mode="human",
        )
    except Exception as e:
        print(f"Error creating environment: {e}")
        print("\nMake sure pygame is installed:")
        print("  pip install pygame")
        return 1

    if args.seed is not None:
        env.reset(seed=args.seed)

    # Run episodes
    try:
        run_visual_episodes(
            model=model,
            env=env,
            num_episodes=args.episodes,
            fps=args.fps,
            deterministic=not args.stochastic,
        )
    finally:
        env.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
