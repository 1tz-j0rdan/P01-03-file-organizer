# P01-03 — File Organizer

A safe-by-default command-line tool that organizes **top-level files** in a chosen folder into category subfolders. Built for Phase 1 of a software engineering portfolio.

## Features

- **Preview by default**: nothing moves without `--apply`.
- Groups files into Images, Documents, Spreadsheets, Presentations, Audio, Video, Archives, Code, and Other.
- Handles file extensions case-insensitively.
- Renames destination collisions (`photo (1).jpg`) rather than overwriting existing files.
- Skips directories and symlinks; ignores dotfiles by default.
- No recursive scanning; no deletion of file contents.
- Unit tests and GitHub Actions CI.

## Windows PowerShell setup

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Usage

**Always start with a disposable test folder, not Downloads or Documents.**

```powershell
New-Item -ItemType Directory -Force .\demo-files
Set-Content .\demo-files\photo.jpg "sample image placeholder"
Set-Content .\demo-files\notes.txt "sample notes"
Set-Content .\demo-files\data.csv "a,b"
python -m file_organizer .\demo-files
python -m file_organizer .\demo-files --apply
```

> The demo `.jpg` is only a placeholder text file used to test classification; it is not a real image.

For a real folder:

```powershell
python -m file_organizer "C:\path\to\folder"
python -m file_organizer "C:\path\to\folder" --apply
```

Include hidden dotfiles if desired:

```powershell
python -m file_organizer .\demo-files --include-hidden
```

## Run checks

```powershell
python -m pytest -v
python -m ruff check .
```

## Safety and limitations

- Uses hard links then unlinks originals, so source and destination must be on the same filesystem. This preserves file bytes but may not work on all filesystems or with certain permissions.
- Does not follow symlinks, process nested folders, or attempt to restore already moved files if a later operation fails.
- Other processes changing files during execution may cause a partial run; back up important data before organizing.
- Designed for local learning, not for concurrent multi-user directories or cloud-sync folders.
