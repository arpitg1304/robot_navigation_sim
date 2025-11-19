"""Train on multiple maps for better generalization.

This script trains a single policy across multiple maps to learn
general navigation skills instead of memorizing one map.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.environment import Environment
from src.gym_env import ReactiveNavEnv


def create_multi_map_env(maps=None, action_type="discrete", max_steps=500):
    """
    Create environment that randomly switches between maps each episode.

    This forces the agent to learn general navigation skills.
    """
    if maps is None:
        maps = Environment.get_available_maps()

    class MultiMapEnv(ReactiveNavEnv):
        """Environment that randomly selects a map on each reset."""

        def __init__(self, map_list, **kwargs):
            self.map_list = map_list
            self.current_map_idx = 0
            # Initialize with first map
            super().__init__(map_name=map_list[0], **kwargs)

        def reset(self, seed=None, options=None):
            """Reset and randomly select a new map."""
            # Randomly pick a map
            self.current_map_idx = np.random.randint(len(self.map_list))
            self.map_name = self.map_list[self.current_map_idx]

            # Load the new map
            self.environment.load_map(self.map_name)
            self.robot_x, self.robot_y = self.environment.robot_start

            return super().reset(seed=seed, options=options)

    return MultiMapEnv(
        map_list=maps,
        action_type=action_type,
        max_steps=max_steps,
        render_mode=None,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Train on multiple maps for generalization"
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=200000,
        help="Total timesteps (default: 200000)",
    )
    parser.add_argument(
        "--maps",
        type=str,
        nargs="+",
        default=None,
        help="Maps to train on (default: all maps)",
    )
    parser.add_argument(
        "--action-type",
        type=str,
        default="discrete",
        choices=["discrete", "continuous"],
        help="Action space type",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="ppo_multi_map.zip",
        help="Output model name",
    )

    args = parser.parse_args()

    # Get maps
    if args.maps is None:
        maps = Environment.get_available_maps()
    else:
        maps = args.maps

    print("=" * 70)
    print("MULTI-MAP TRAINING")
    print("=" * 70)
    print(f"Training on maps: {maps}")
    print(f"Action type: {args.action_type}")
    print(f"Total timesteps: {args.timesteps:,}")
    print(f"Output: models/{args.model_name}")
    print("=" * 70)
    print()

    # Create multi-map environment
    env = create_multi_map_env(
        maps=maps,
        action_type=args.action_type,
        max_steps=500,
    )

    # Train with Stable-Baselines3
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_checker import check_env

        print("Checking environment...")
        check_env(env, warn=True)
        print("✓ Environment valid\n")

        print("Creating PPO model...")
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
            ent_coef=0.01,  # Encourage exploration
        )

        print(f"\nTraining for {args.timesteps:,} timesteps...")
        print("(Map changes randomly each episode for generalization)\n")

        model.learn(total_timesteps=args.timesteps, progress_bar=True)

        # Save
        Path("models").mkdir(exist_ok=True)
        model_path = Path("models") / args.model_name
        model.save(str(model_path))

        print(f"\n✓ Training complete!")
        print(f"Model saved to: {model_path}")
        print("\nThis model should generalize across all maps!")
        print("\nTest on each map:")
        for map_name in maps:
            print(f"  python rl/test_policy_headless.py --model {model_path} --map {map_name} --episodes 50")

    except ImportError:
        print("Error: stable-baselines3 not installed")
        print("Install with: pip install stable-baselines3")
        return 1

    env.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
