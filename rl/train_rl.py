"""Example training script for the reactive navigation RL environment.

This demonstrates how to use the ReactiveNavEnv with popular RL libraries.
"""

import argparse
from pathlib import Path

import numpy as np

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gym_env import ReactiveNavEnv


def random_agent_demo(env: ReactiveNavEnv, num_episodes: int = 5):
    """
    Run a random agent to demonstrate the environment API.

    Args:
        env: The environment instance
        num_episodes: Number of episodes to run
    """
    print("\n" + "=" * 60)
    print("Random Agent Demo")
    print("=" * 60)

    episode_rewards = []
    episode_lengths = []
    successes = 0

    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        step_count = 0
        done = False

        while not done:
            # Random action
            action = env.action_space.sample()

            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            step_count += 1
            done = terminated or truncated

            if terminated and info.get("goal_reached", False):
                successes += 1

        episode_rewards.append(episode_reward)
        episode_lengths.append(step_count)

        print(
            f"Episode {episode + 1}/{num_episodes}: "
            f"Reward={episode_reward:.2f}, Steps={step_count}, "
            f"Goal={'✓' if info.get('goal_reached', False) else '✗'}"
        )

    print(f"\nSummary:")
    print(f"  Average Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"  Average Steps: {np.mean(episode_lengths):.1f} ± {np.std(episode_lengths):.1f}")
    print(f"  Success Rate: {successes}/{num_episodes} ({100*successes/num_episodes:.1f}%)")


def stable_baselines3_demo(env: ReactiveNavEnv, total_timesteps: int = 50000):
    """
    Train using Stable-Baselines3 (PPO algorithm).

    Args:
        env: The environment instance
        total_timesteps: Total training timesteps
    """
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_checker import check_env
    except ImportError:
        print("\nStable-Baselines3 not installed. Install with:")
        print("  pip install stable-baselines3")
        return

    print("\n" + "=" * 60)
    print("Stable-Baselines3 PPO Training")
    print("=" * 60)

    # Check environment
    print("Checking environment compatibility...")
    check_env(env, warn=True)
    print("✓ Environment is compatible!\n")

    # Create PPO agent
    print("Creating PPO agent...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
    )

    # Train
    print(f"\nTraining for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps, progress_bar=True)

    # Save model
    model_path = Path("models") / "ppo_reactive_nav.zip"
    model_path.parent.mkdir(exist_ok=True)
    model.save(str(model_path))
    print(f"\n✓ Model saved to {model_path}")

    # Evaluate
    print("\nEvaluating trained agent...")
    evaluate_agent(env, model, num_episodes=10)


def evaluate_agent(env: ReactiveNavEnv, model, num_episodes: int = 10):
    """
    Evaluate a trained agent.

    Args:
        env: The environment instance
        model: Trained model (must have .predict() method)
        num_episodes: Number of evaluation episodes
    """
    episode_rewards = []
    episode_lengths = []
    successes = 0

    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        step_count = 0
        done = False

        while not done:
            # Get action from model
            action, _ = model.predict(obs, deterministic=True)

            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            step_count += 1
            done = terminated or truncated

            if terminated and info.get("goal_reached", False):
                successes += 1

        episode_rewards.append(episode_reward)
        episode_lengths.append(step_count)

        print(
            f"Episode {episode + 1}/{num_episodes}: "
            f"Reward={episode_reward:.2f}, Steps={step_count}, "
            f"Goal={'✓' if info.get('goal_reached', False) else '✗'}"
        )

    print(f"\nEvaluation Summary:")
    print(f"  Average Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"  Average Steps: {np.mean(episode_lengths):.1f} ± {np.std(episode_lengths):.1f}")
    print(f"  Success Rate: {successes}/{num_episodes} ({100*successes/num_episodes:.1f}%)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Train RL agent for reactive navigation")
    parser.add_argument(
        "--mode",
        type=str,
        default="random",
        choices=["random", "sb3"],
        help="Training mode: random (baseline) or sb3 (Stable-Baselines3)",
    )
    parser.add_argument(
        "--action-type",
        type=str,
        default="discrete",
        choices=["discrete", "continuous"],
        help="Action space type",
    )
    parser.add_argument(
        "--map",
        type=str,
        default="custom_map",
        help="Map name to use for training",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=5,
        help="Number of episodes (for random agent)",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=50000,
        help="Total timesteps (for SB3 training)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=500,
        help="Maximum steps per episode",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Enable rendering (warning: slows down training)",
    )

    args = parser.parse_args()

    # Create environment
    env = ReactiveNavEnv(
        map_name=args.map,
        max_steps=args.max_steps,
        action_type=args.action_type,
        render_mode="human" if args.render else None,
    )

    print(f"\n{'='*60}")
    print(f"Environment Configuration")
    print(f"{'='*60}")
    print(f"  Map: {args.map}")
    print(f"  Action Space: {args.action_type}")
    print(f"  Observation Space: {env.observation_space.shape}")
    print(f"  Max Steps: {args.max_steps}")
    print(f"  Render: {args.render}")

    # Run selected mode
    if args.mode == "random":
        random_agent_demo(env, num_episodes=args.episodes)
    elif args.mode == "sb3":
        stable_baselines3_demo(env, total_timesteps=args.timesteps)

    env.close()
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
