import argparse
from pathlib import Path
from devguard.agent import DevGuardAgent
from devguard.retriever import LocalRetriever
from devguard.config import load_config


def save_report(content: str, output_path: str) -> None:
    path = Path(output_path)
    if path.suffix.lower() == ".html":
        # Wrap content in basic styled HTML template
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DevGuard Security Audit Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #0d1117; color: #c9d1d9; }}
        h1, h2, h3 {{ color: #58a6ff; }}
        pre {{ background: #161b22; padding: 16px; border-radius: 6px; overflow-x: auto; }}
        code {{ font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace; }}
    </style>
</head>
<body>
    <h1>DevGuard Security Audit Report</h1>
    <hr>
    <div><pre>{content}</pre></div>
</body>
</html>"""
        path.write_text(html_content, encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")
    print(f"Report saved successfully to {path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="DevGuard - AI-Powered Code Security Auditor")
    parser.add_argument("--dir", default=".", help="Target repository directory to audit")
    parser.add_argument("--output", "-o", help="Path to save output report (.md or .html)")
    
    args = parser.parse_args()
    
    config = load_config(args.dir)

    retriever = LocalRetriever(root_dir=args.dir, ignore_dirs=config.get("ignore_dirs"))
    indexed_files = retriever.scan_directory()
    
    agent = DevGuardAgent()
    report = agent.analyze_repository(indexed_files)
    
    print("\n--- DevGuard Audit Results ---\n")
    print(report)
    
    if args.output:
        save_report(report, args.output)


if __name__ == "__main__":
    main()