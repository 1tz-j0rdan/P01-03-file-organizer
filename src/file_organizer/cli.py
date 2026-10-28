"""Command-line entry point."""

import argparse
from pathlib import Path

from .core import build_plan, execute_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Organize top-level files by category")
    parser.add_argument("directory", type=Path, help="Directory to organize")
    parser.add_argument("--apply", action="store_true", help="Actually move files (default: preview)")
    parser.add_argument("--include-hidden", action="store_true", help="Include dotfiles")
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.directory, include_hidden=args.include_hidden)
        if not plan:
            print("No eligible files found.")
            return 0
        print(f"{'Applying' if args.apply else 'Previewing'} {len(plan)} file(s):")
        for item in plan:
            print(f"  {item.source.name} -> {item.destination.parent.name}/{item.destination.name}")
        if args.apply:
            completed = execute_plan(plan)
            print(f"Moved {len(completed)} file(s).")
        else:
            print("Preview only. Add --apply to move files.")
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
