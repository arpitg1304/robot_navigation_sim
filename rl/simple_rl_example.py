"""Minimal example showing how to use the RL environment.

This is the simplest possible example to get started.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gym_env import ReactiveNavEnv


def main():
    """Run a simple episode with random actions."""
    # Create environment
    env = ReactiveNavEnv(
        map_name="custom_map",
        action_type="discrete",  # or "continuous"
        max_steps=500,
    )

    print("Running 5 episodes with random actions...\n")

    for episode in range(5):
        # Reset environment
        observation, info = env.reset()

        episode_reward = 0
        step = 0
        done = False

        # Run episode
        while not done:
            # Take random action
            action = env.action_space.sample()

            # Step environment
            observation, reward, terminated, truncated, info = env.step(action)

            episode_reward += reward
            step += 1
            done = terminated or truncated

        # Print results
        goal_status = "✓ SUCCESS" if info.get("goal_reached", False) else "✗ Failed"
        collision_status = " (collision)" if info.get("collision", False) else ""

        print(
            f"Episode {episode + 1}: "
            f"{goal_status}{collision_status} | "
            f"Reward: {episode_reward:6.2f} | "
            f"Steps: {step:3d} | "
            f"Final distance: {info['distance_to_goal']:.1f}"
        )

    env.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
