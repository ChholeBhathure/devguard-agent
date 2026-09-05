import argparse
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from devguard.retriever import LocalRetriever
from devguard.agent import DevGuardAgent

#Initializes Rich Console for styled terminal printing
console = Console()

def main():
    """Command-line interface entry point for DevGuard."""
    parser = argparse.ArgumentParser(description="DevGuard: Local-first autonomous Python code review agent.")
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to the directory or file you want DevGuard to review(default: current directory)."
    )
    args = parser.parse_args()

    # 2. Display a welcome header banner
    console.print(
        Panel.fit(
            "[bold cyan]DevGuard Agent[/bold cyan]\n[dim]Autonomous AI Security & Code Reviewer[/dim]",
            border_style="cyan",)
    )
    # 3. Step 1: Scan Directory with a loading status animation
    with console.status("[bold green]Scanning codebase AST structure...", spinner="dots"):
        try:
            retriever = LocalRetriever(root_dir=args.path)
            index = retriever.scan_directory()
        except Exception as e:
            console.print(f"[bold red]Error during directory scanning:[/bold red] {e}")
            sys.exit(1)

    console.print(f"[bold green]√[/bold green] Successfully scanned [bold]{len(index)}[/bold] Python file(s).\n")
    # 4. Step 2: Send Context to Gemini AI Agent
    with console.status("[bold blue]Analyzing code with Gemini AI...", spinner="earth"):
        try:
            agent = DevGuardAgent()
            review_result = agent.review_codebase(index)
        except Exception as e:
            console.print(f"[bold red]Error calling Gemini API:[/bold red] {e}")
            sys.exit(1)
    # 5. Render Gemini's response as formatted Markdown
    console.print(Panel("[bold yellow]Audit Response & Code Review[/bold yellow]", border_style="yellow"))
    console.print(Markdown(review_result))

if __name__ == "__main__":
    main()