"""Terminal User Interface for RL Training and Testing.

A simple, interactive TUI for training and testing RL navigation policies.

Usage:
    python rl_tui.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    from rich.layout import Layout
    from rich.live import Live
except ImportError:
    print("Error: 'rich' library not installed")
    print("Install with: pip install rich")
    sys.exit(1)

from src.environment import Environment
from src.gym_env import ReactiveNavEnv


console = Console()


def get_available_maps():
    """Get list of available maps."""
    return Environment.get_available_maps()


def get_available_models():
    """Get list of trained models."""
    models_dir = Path("models")
    if not models_dir.exists():
        return []

    models = list(models_dir.glob("*.zip"))
    return [m.name for m in sorted(models, key=lambda x: x.stat().st_mtime, reverse=True)]


def show_header():
    """Display application header."""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]🤖 RL Navigation Training & Testing[/bold cyan]\n"
        "[dim]Interactive Terminal Interface[/dim]",
        border_style="cyan"
    ))
    console.print()


def show_models():
    """Display available models."""
    models = get_available_models()

    if not models:
        console.print("[yellow]No trained models found in models/ directory[/yellow]")
        console.print("[dim]Train a model first from the Training menu[/dim]\n")
        return

    table = Table(title="Available Models", box=box.ROUNDED)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Model Name", style="green")
    table.add_column("Size", justify="right")

    for i, model in enumerate(models, 1):
        model_path = Path("models") / model
        size_kb = model_path.stat().st_size / 1024
        table.add_row(str(i), model, f"{size_kb:.1f} KB")

    console.print(table)
    console.print()


def select_map():
    """Interactive map selection."""
    maps = get_available_maps()

    console.print("[bold]Available Maps:[/bold]")
    for i, map_name in enumerate(maps, 1):
        console.print(f"  {i}. [cyan]{map_name}[/cyan]")

    while True:
        choice = Prompt.ask(
            "\nSelect map",
            choices=[str(i) for i in range(1, len(maps) + 1)],
            default="1"
        )
        return maps[int(choice) - 1]


def select_model():
    """Interactive model selection."""
    models = get_available_models()

    if not models:
        console.print("[red]No models found! Train a model first.[/red]")
        return None

    console.print("[bold]Available Models:[/bold]")
    for i, model in enumerate(models, 1):
        console.print(f"  {i}. [cyan]{model}[/cyan]")

    while True:
        choice = Prompt.ask(
            "\nSelect model",
            choices=[str(i) for i in range(1, len(models) + 1)],
            default="1"
        )
        return models[int(choice) - 1]


def train_menu():
    """Training menu."""
    show_header()
    console.print(Panel("[bold green]Training Mode[/bold green]", border_style="green"))
    console.print()

    # Training type
    console.print("[bold]Training Type:[/bold]")
    console.print("  1. [cyan]Single Map[/cyan] - Train on one map (may overfit)")
    console.print("  2. [green]Multi-Map[/green] - Train on multiple maps (generalizes better)")

    training_type = Prompt.ask("\nSelect training type", choices=["1", "2"], default="2")
    multi_map = training_type == "2"
    console.print()

    # Select map(s)
    if multi_map:
        maps = get_available_maps()
        console.print("[bold]Select Maps for Multi-Map Training:[/bold]")
        console.print("  1. [cyan]All maps[/cyan] (best generalization)")
        console.print("  2. [cyan]Diverse set (6 maps)[/cyan] - open_field→mixed_complexity")
        console.print("  3. [cyan]All except challenge[/cyan] (easier training)")
        console.print("  4. [cyan]Custom selection[/cyan]")

        map_choice = Prompt.ask("\nSelect maps", choices=["1", "2", "3", "4"], default="2")

        if map_choice == "1":
            selected_maps = maps
        elif map_choice == "2":
            # Diverse training set (curated for generalization)
            diverse_maps = ['open_field', 'scattered_rocks', 'narrow_corridors',
                           'dense_forest', 'u_shaped_trap', 'mixed_complexity']
            selected_maps = [m for m in diverse_maps if m in maps]
        elif map_choice == "3":
            selected_maps = [m for m in maps if m != "challenge"]
        else:
            console.print("\nAvailable maps:")
            for i, m in enumerate(maps, 1):
                console.print(f"  {i}. {m}")
            indices = Prompt.ask("\nEnter map numbers (comma-separated)", default="1,2,3")
            selected_maps = [maps[int(i)-1] for i in indices.split(",")]

        console.print(f"✓ Selected maps: [cyan]{', '.join(selected_maps)}[/cyan]\n")
        map_name = "multi"  # For naming
    else:
        map_name = select_map()
        selected_maps = [map_name]
        console.print(f"✓ Selected map: [cyan]{map_name}[/cyan]\n")

    # Select action type
    console.print("[bold]Action Type:[/bold]")
    console.print("  1. [cyan]Discrete[/cyan] (turn_left, go_straight, turn_right)")
    console.print("  2. [cyan]Continuous[/cyan] (linear_vel, angular_vel)")
    action_choice = Prompt.ask("\nSelect action type", choices=["1", "2"], default="1")
    action_type = "discrete" if action_choice == "1" else "continuous"
    console.print(f"✓ Action type: [cyan]{action_type}[/cyan]\n")

    # Timesteps
    console.print("[bold]Training Duration:[/bold]")
    console.print("  1. Quick test (10k steps, ~1 min)")
    console.print("  2. Short (50k steps, ~3 min)")
    console.print("  3. Medium (100k steps, ~5 min)")
    console.print("  4. Long (200k steps, ~10 min)")
    console.print("  5. Custom")

    duration_choice = Prompt.ask("\nSelect duration", choices=["1", "2", "3", "4", "5"], default="2")

    timesteps_map = {"1": 10000, "2": 50000, "3": 100000, "4": 200000}
    if duration_choice in timesteps_map:
        timesteps = timesteps_map[duration_choice]
    else:
        timesteps = int(Prompt.ask("Enter timesteps", default="50000"))

    console.print(f"✓ Timesteps: [cyan]{timesteps:,}[/cyan]\n")

    # Model name
    if multi_map:
        default_name = f"ppo_multimap_{action_type}.zip"
    else:
        default_name = f"ppo_{map_name}_{action_type}.zip"
    model_name = Prompt.ask("Model name", default=default_name)
    console.print()

    # Confirm
    console.print("[bold yellow]Training Configuration:[/bold yellow]")
    if multi_map:
        console.print(f"  Maps: {', '.join(selected_maps)}")
        console.print(f"  Mode: [green]Multi-Map (generalizes)[/green]")
    else:
        console.print(f"  Map: {map_name}")
        console.print(f"  Mode: Single Map")
    console.print(f"  Action Type: {action_type}")
    console.print(f"  Timesteps: {timesteps:,}")
    console.print(f"  Model: {model_name}")
    console.print()

    if not Confirm.ask("Start training?", default=True):
        console.print("[yellow]Training cancelled[/yellow]")
        return

    # Train
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.env_checker import check_env
    except ImportError:
        console.print("[red]Error: stable-baselines3 not installed[/red]")
        console.print("Install with: [cyan]pip install stable-baselines3[/cyan]")
        return

    console.print("\n[bold green]Starting training...[/bold green]\n")

    # Create environment
    if multi_map:
        # Multi-map environment
        import numpy as np

        class MultiMapEnv(ReactiveNavEnv):
            """Environment that randomly selects a map on each reset."""

            def __init__(self, map_list, **kwargs):
                self.map_list = map_list
                super().__init__(map_name=map_list[0], **kwargs)

            def reset(self, seed=None, options=None):
                """Reset and randomly select a new map."""
                self.map_name = np.random.choice(self.map_list)
                self.environment.load_map(self.map_name)
                self.robot_x, self.robot_y = self.environment.robot_start
                return super().reset(seed=seed, options=options)

        env = MultiMapEnv(
            map_list=selected_maps,
            action_type=action_type,
            max_steps=500,
            render_mode=None,
        )
        console.print(f"[dim]Multi-map training: map changes randomly each episode[/dim]\n")
    else:
        env = ReactiveNavEnv(
            map_name=map_name,
            action_type=action_type,
            max_steps=500,
            render_mode=None,
        )

    # Create model
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
    )

    # Train
    model.learn(total_timesteps=timesteps, progress_bar=True)

    # Save
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / model_name
    model.save(str(model_path))

    env.close()

    console.print(f"\n[bold green]✓ Training complete![/bold green]")
    console.print(f"Model saved to: [cyan]{model_path}[/cyan]\n")

    if multi_map:
        console.print("[bold]This model trained on multiple maps![/bold]")
        console.print("[green]✓[/green] Should generalize across different maps")
        console.print("\nTest it on each map:")
        for test_map in selected_maps:
            console.print(f"  • {test_map}")
    else:
        console.print("[yellow]Note:[/yellow] Trained on single map - may not generalize well")
        console.print("Consider multi-map training for better generalization")

    console.print()
    Prompt.ask("Press Enter to continue")


def test_menu():
    """Testing menu."""
    show_header()
    console.print(Panel("[bold blue]Testing Mode[/bold blue]", border_style="blue"))
    console.print()

    # Show and select model
    show_models()
    model_name = select_model()

    if model_name is None:
        Prompt.ask("Press Enter to continue")
        return

    console.print(f"✓ Selected model: [cyan]{model_name}[/cyan]\n")

    # Select map
    map_name = select_map()
    console.print(f"✓ Selected map: [cyan]{map_name}[/cyan]\n")

    # Test mode
    console.print("[bold]Test Mode:[/bold]")
    console.print("  1. [cyan]Headless[/cyan] (fast, comprehensive stats)")
    console.print("  2. [cyan]Visual[/cyan] (watch the agent navigate)")

    test_mode = Prompt.ask("\nSelect mode", choices=["1", "2"], default="2")
    visual = test_mode == "2"

    # Episodes
    if visual:
        default_episodes = "10"
    else:
        default_episodes = "100"

    episodes = int(Prompt.ask("Number of episodes", default=default_episodes))
    console.print()

    # Load model
    try:
        from stable_baselines3 import PPO
    except ImportError:
        console.print("[red]Error: stable-baselines3 not installed[/red]")
        Prompt.ask("Press Enter to continue")
        return

    model_path = Path("models") / model_name
    console.print(f"[dim]Loading model...[/dim]")
    model = PPO.load(str(model_path))
    console.print("[green]✓ Model loaded[/green]\n")

    # Create environment
    env = ReactiveNavEnv(
        map_name=map_name,
        max_steps=500,
        render_mode="human" if visual else None,
    )

    # Run episodes
    console.print(f"[bold]Running {episodes} episodes...[/bold]\n")

    import time
    import numpy as np

    successes = 0
    collisions = 0
    timeouts = 0
    rewards = []
    steps_list = []

    for episode in range(episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated

            if visual:
                env.render()
                time.sleep(1/30)  # 30 FPS

        rewards.append(episode_reward)
        steps_list.append(steps)

        if terminated:
            if info.get("goal_reached", False):
                successes += 1
                status = "[green]SUCCESS ✓[/green]"
            else:
                collisions += 1
                status = "[red]COLLISION ✗[/red]"
        else:
            timeouts += 1
            status = "[yellow]TIMEOUT ⏱[/yellow]"

        console.print(
            f"Episode {episode + 1:3d}/{episodes}: {status} | "
            f"Reward: {episode_reward:7.2f} | Steps: {steps:3d}"
        )

        if visual:
            time.sleep(0.5)

    env.close()

    # Show statistics
    console.print()
    console.print(Panel.fit(
        f"[bold]Test Results[/bold]\n\n"
        f"Success Rate:  [green]{successes/episodes:6.1%}[/green] ({successes}/{episodes})\n"
        f"Collision Rate: [red]{collisions/episodes:6.1%}[/red] ({collisions}/{episodes})\n"
        f"Timeout Rate:  [yellow]{timeouts/episodes:6.1%}[/yellow] ({timeouts}/{episodes})\n\n"
        f"Avg Reward:    {np.mean(rewards):7.2f} ± {np.std(rewards):.2f}\n"
        f"Avg Steps:     {np.mean(steps_list):7.1f} ± {np.std(steps_list):.1f}",
        border_style="blue"
    ))
    console.print()

    Prompt.ask("Press Enter to continue")


def random_baseline_menu():
    """Random baseline testing."""
    show_header()
    console.print(Panel("[bold magenta]Random Baseline[/bold magenta]", border_style="magenta"))
    console.print()

    # Select map
    map_name = select_map()
    console.print(f"✓ Selected map: [cyan]{map_name}[/cyan]\n")

    # Visual or headless
    visual = Confirm.ask("Show visualization?", default=False)

    episodes = int(Prompt.ask("Number of episodes", default="50"))
    console.print()

    # Create environment
    env = ReactiveNavEnv(
        map_name=map_name,
        max_steps=500,
        render_mode="human" if visual else None,
    )

    # Run episodes
    console.print(f"[bold]Running {episodes} random episodes...[/bold]\n")

    import time
    import numpy as np

    successes = 0
    collisions = 0
    timeouts = 0
    rewards = []
    steps_list = []

    for episode in range(episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        done = False

        while not done:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated

            if visual:
                env.render()
                time.sleep(1/60)

        rewards.append(episode_reward)
        steps_list.append(steps)

        if terminated:
            if info.get("goal_reached", False):
                successes += 1
                status = "[green]SUCCESS ✓[/green]"
            else:
                collisions += 1
                status = "[red]COLLISION ✗[/red]"
        else:
            timeouts += 1
            status = "[yellow]TIMEOUT ⏱[/yellow]"

        if episode % 10 == 0 or episode == episodes - 1:
            console.print(
                f"Episode {episode + 1:3d}/{episodes}: {status} | "
                f"Reward: {episode_reward:7.2f} | Steps: {steps:3d}"
            )

        if visual:
            time.sleep(0.3)

    env.close()

    # Show statistics
    console.print()
    console.print(Panel.fit(
        f"[bold]Random Baseline Results[/bold]\n\n"
        f"Success Rate:  [green]{successes/episodes:6.1%}[/green] ({successes}/{episodes})\n"
        f"Collision Rate: [red]{collisions/episodes:6.1%}[/red] ({collisions}/{episodes})\n"
        f"Timeout Rate:  [yellow]{timeouts/episodes:6.1%}[/yellow] ({timeouts}/{episodes})\n\n"
        f"Avg Reward:    {np.mean(rewards):7.2f} ± {np.std(rewards):.2f}\n"
        f"Avg Steps:     {np.mean(steps_list):7.1f} ± {np.std(steps_list):.1f}",
        border_style="magenta"
    ))
    console.print()

    Prompt.ask("Press Enter to continue")


def main_menu():
    """Main menu loop."""
    while True:
        show_header()

        # Show models
        show_models()

        # Main menu
        console.print("[bold]Main Menu:[/bold]")
        console.print("  1. [green]Train[/green] - Train a new RL agent")
        console.print("  2. [blue]Test[/blue] - Test a trained agent")
        console.print("  3. [magenta]Baseline[/magenta] - Run random baseline")
        console.print("  4. [red]Quit[/red]")
        console.print()

        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            train_menu()
        elif choice == "2":
            test_menu()
        elif choice == "3":
            random_baseline_menu()
        elif choice == "4":
            console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
            break


def main():
    """Entry point."""
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
