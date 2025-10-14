"""
Enhanced CLI with Rich UI.
Provides interactive terminal interface with progress bars and wizards.
"""

from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint


class EnhancedCLI:
    """
    Enhanced command-line interface with rich terminal UI.
    Provides progress bars, tables, and interactive wizards.
    """
    
    def __init__(self):
        """Initialize enhanced CLI."""
        self.console = Console()
    
    def show_banner(self) -> None:
        """Display application banner."""
        banner = """
  █████╗  ██████╗ ██████╗███████╗██╗     ███████╗██████╗  █████╗ ██████╗ ██████╗ 
 ██╔══██╗██╔════╝██╔════╝██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
 ███████║██║     ██║     █████╗  ██║     █████╗  ██████╔╝███████║██████╔╝██████╔╝
 ██╔══██║██║     ██║     ██╔══╝  ██║     ██╔══╝  ██╔══██╗██╔══██║██╔═══╝ ██╔═══╝ 
 ██║  ██║╚██████╗╚██████╗███████╗███████╗███████╗██║  ██║██║  ██║██║     ██║     
 ╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     
        """
        self.console.print(banner, style="bold cyan")
        self.console.print(
            "Next Generation Hardware Control Platform",
            style="bold white",
            justify="center"
        )
        self.console.print()
    
    def show_progress(
        self,
        tasks: List[Dict[str, Any]],
        description: str = "Processing"
    ) -> None:
        """
        Display progress bar for tasks.
        
        Args:
            tasks: List of task dictionaries with 'name' and 'work' callable
            description: Progress description
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            for task_info in tasks:
                task = progress.add_task(
                    task_info.get("name", "Task"),
                    total=100
                )
                
                # Simulate work (in real usage, this would be actual work)
                for i in range(100):
                    progress.update(task, advance=1)
                    if "work" in task_info and callable(task_info["work"]):
                        task_info["work"]()
    
    def show_table(
        self,
        title: str,
        columns: List[str],
        rows: List[List[Any]]
    ) -> None:
        """
        Display formatted table.
        
        Args:
            title: Table title
            columns: Column headers
            rows: Table rows
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        for column in columns:
            table.add_column(column)
        
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        self.console.print(table)
    
    def show_panel(self, content: str, title: str, style: str = "blue") -> None:
        """
        Display content in a panel.
        
        Args:
            content: Panel content
            title: Panel title
            style: Panel style
        """
        panel = Panel(content, title=title, border_style=style)
        self.console.print(panel)
    
    def show_tree(self, title: str, structure: Dict[str, Any]) -> None:
        """
        Display hierarchical tree structure.
        
        Args:
            title: Tree title
            structure: Hierarchical structure dictionary
        """
        tree = Tree(f"[bold]{title}[/bold]")
        self._build_tree(tree, structure)
        self.console.print(tree)
    
    def _build_tree(self, parent, structure: Dict[str, Any]) -> None:
        """Recursively build tree structure."""
        for key, value in structure.items():
            if isinstance(value, dict):
                branch = parent.add(f"[cyan]{key}[/cyan]")
                self._build_tree(branch, value)
            elif isinstance(value, list):
                branch = parent.add(f"[cyan]{key}[/cyan]")
                for item in value:
                    branch.add(f"[green]• {item}[/green]")
            else:
                parent.add(f"[yellow]{key}[/yellow]: [white]{value}[/white]")
    
    def prompt_user(self, question: str, default: Optional[str] = None) -> str:
        """
        Prompt user for input.
        
        Args:
            question: Question to ask
            default: Default value
            
        Returns:
            User input string
        """
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "
        
        return self.console.input(prompt) or default or ""
    
    def confirm(self, question: str, default: bool = False) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            question: Question to ask
            default: Default value
            
        Returns:
            True if confirmed, False otherwise
        """
        suffix = " [Y/n]" if default else " [y/N]"
        response = self.console.input(question + suffix + ": ").lower()
        
        if not response:
            return default
        
        return response in ["y", "yes"]
    
    def show_success(self, message: str) -> None:
        """Display success message."""
        self.console.print(f"✓ {message}", style="bold green")
    
    def show_error(self, message: str) -> None:
        """Display error message."""
        self.console.print(f"✗ {message}", style="bold red")
    
    def show_warning(self, message: str) -> None:
        """Display warning message."""
        self.console.print(f"⚠ {message}", style="bold yellow")
    
    def show_info(self, message: str) -> None:
        """Display info message."""
        self.console.print(f"ℹ {message}", style="bold blue")
    
    def wizard_project_setup(self) -> Dict[str, Any]:
        """
        Interactive project setup wizard.
        
        Returns:
            Dictionary with project configuration
        """
        self.console.rule("[bold]Project Setup Wizard[/bold]")
        
        config = {}
        
        # Project name
        config["project_name"] = self.prompt_user(
            "Project name",
            "my-accelerapp-project"
        )
        
        # Platform selection
        self.console.print("\nSelect target platform:")
        platforms = ["Arduino", "ESP32", "STM32", "MicroPython", "Raspberry Pi"]
        for i, platform in enumerate(platforms, 1):
            self.console.print(f"  {i}. {platform}")
        
        platform_choice = self.prompt_user("Platform choice", "2")
        config["platform"] = platforms[int(platform_choice) - 1].lower()
        
        # Features
        self.console.print("\nSelect features (comma-separated):")
        features = ["WiFi", "Bluetooth", "Camera", "Sensors", "Actuators"]
        for i, feature in enumerate(features, 1):
            self.console.print(f"  {i}. {feature}")
        
        feature_choices = self.prompt_user("Features", "1,4")
        selected_features = [
            features[int(i.strip()) - 1]
            for i in feature_choices.split(",")
            if i.strip().isdigit()
        ]
        config["features"] = selected_features
        
        # Output directory
        config["output_dir"] = self.prompt_user(
            "Output directory",
            "./generated"
        )
        
        # Show summary
        self.console.print("\n[bold]Configuration Summary:[/bold]")
        self.show_tree("Project Configuration", config)
        
        if self.confirm("\nProceed with this configuration?", default=True):
            return config
        else:
            return {}
    
    def display_generation_results(self, results: Dict[str, Any]) -> None:
        """
        Display code generation results.
        
        Args:
            results: Generation results dictionary
        """
        self.console.rule("[bold green]Generation Results[/bold green]")
        
        # Show summary table
        summary_data = [
            ["Firmware", results.get("firmware_files", 0), "files"],
            ["Software SDKs", results.get("sdk_files", 0), "files"],
            ["UI Components", results.get("ui_files", 0), "files"],
            ["Tests", results.get("test_files", 0), "files"],
        ]
        
        self.show_table(
            "Generated Code Summary",
            ["Component", "Count", "Unit"],
            summary_data
        )
        
        # Show file tree
        if "file_tree" in results:
            self.show_tree("Generated Files", results["file_tree"])
        
        self.show_success(f"Code generated successfully in {results.get('output_dir', 'output')}")
