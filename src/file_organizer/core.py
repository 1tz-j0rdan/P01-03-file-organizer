"""Plan and safely organize files in a single directory."""

import os
from dataclasses import dataclass
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "Spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg"},
    "Video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Archives": {".zip", ".tar", ".gz", ".7z", ".rar"},
    "Code": {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".json", ".xml"},
}


@dataclass(frozen=True)
class PlanItem:
    source: Path
    destination: Path


def category_for(path: Path) -> str:
    """Return category based on a file's last suffix."""
    suffix = path.suffix.lower()
    return next((name for name, extensions in CATEGORIES.items() if suffix in extensions), "Other")


def _unique_destination(target: Path, reserved: set[Path]) -> Path:
    candidate = target
    number = 1
    while candidate.exists() or candidate in reserved:
        candidate = target.with_name(f"{target.stem} ({number}){target.suffix}")
        number += 1
    return candidate


def build_plan(directory: Path, include_hidden: bool = False) -> list[PlanItem]:
    """Plan moves for immediate regular files only; never follow symlinks."""
    directory = Path(directory).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    reserved: set[Path] = set()
    plan = []
    for source in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if source.is_symlink() or not source.is_file():
            continue
        if source.name.startswith(".") and not include_hidden:
            continue
        target = directory / category_for(source) / source.name
        target = _unique_destination(target, reserved)
        reserved.add(target)
        plan.append(PlanItem(source=source, destination=target))
    return plan


def execute_plan(plan: list[PlanItem]) -> list[PlanItem]:
    """Move planned files without overwriting or following symlinks.

    Revalidate each item immediately before moving; abort on changed targets.
    """
    completed = []
    for item in plan:
        if item.source.is_symlink() or not item.source.is_file():
            raise FileNotFoundError(f"Source no longer a regular file: {item.source}")
        if item.destination.exists() or item.destination.is_symlink():
            raise FileExistsError(f"Destination already exists: {item.destination}")
        if item.destination.parent.is_symlink():
            raise ValueError(f"Destination folder is a symlink: {item.destination.parent}")
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive hard-link reservation avoids accidental overwrite, even after planning.
        # On filesystems where hard links are unsupported, fail rather than risk overwriting.
        os.link(item.source, item.destination, follow_symlinks=False)
        try:
            item.source.unlink()
        except OSError:
            item.destination.unlink()
            raise
        completed.append(item)
    return completed
