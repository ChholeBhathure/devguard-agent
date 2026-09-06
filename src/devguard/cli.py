import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from devguard.retriever import LocalRetriever
from devguard.agent import DevGuardAgent

#Initializes Rich Console for styled terminal printing
console = Console()

def main():
    """Command-line interface entry point for DevGuard."""
    parser = argparse.ArgumentParser(description="DevGuard: Autonomous Local Security Auditor")
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to the directory or file to audit (default: current directory)."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Export security audit results to a file (e.g., report.md or report.html)"
    )
    args = parser.parse_args()
    target_path = Path(args.path).resolve()

    if not target_path.exists():
         print(f"[Error] Target path '{target_path}' does not exist.")
         sys.exit(1)

    console = Console()
    console.print(f"\n[bold green][DevGuard][/bold green] Initializing security audit on: [cyan]{target_path}[/cyan]\n")

    # 1. Scan directory and build context using LocalRetriever
    retriever = LocalRetriever(root_dir=str(target_path))
    context = retriever.scan_directory()

    # 2. Analyze context using DevGuardAgent
    agent = DevGuardAgent()
    report_content = agent.review_codebase(context)

    # 3. Display finding in console
    console.print(Panel(Markdown(report_content), title="[bold yellow]Audit Response & Code Review[/bold yellow]"))

    # 4. Handle File Export
    if args.output:
         output_file = Path(args.output).resolve()
         save_report(report_content, output_file)
def save_report(content: str, output_path: Path):
     """ Saves report content in Markdown or converts simple Markdown to HTML."""
     try:
          if output_path.suffix.lower() == ".html":
               # Simple wrapper to format Markdown cleanly as HTML
               html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DevGuard Security Audit Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 2rem; max-width: 900px; margin; aut0;
               background: #1e1e2e; color: #cdd6f4; }}
        h1, h2, h3 {{ color: #89b4fa; border-bottom: 1px solid #45475a; padding-bottom: 0.3em; }}
        code {{ background: #3131244; padding: 0.2em 0.4em; border-radius: 4px; font-family: monospace; }}
        pre {{ background: #181825; padding: 1em; border-radius: 6px; overflow-x: auto; }}
        ul {{ padding-left: 1.5rem; }}
        blockquote {{ border-left: 4px solid #f38ba8; margin: 0; padding-left: 1rem; color: #f38ba8; }}
    </style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>""" 
               output_path.write_text(html_content, encoding="utf-8")
          else:
                # Default to Markdown export
                output_path.write_text(content, encoding="utf-8")
          print(f"\n✅ Security report successfully exported to: {output_path}")
     except Exception as e:
            print(f"\n❌ Failed to save report to {output_path}: {e}")

if __name__ == "__main__":
    main()

        