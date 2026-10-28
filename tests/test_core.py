from pathlib import Path

import pytest

from file_organizer.cli import main
from file_organizer.core import build_plan, category_for, execute_plan


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("a.JPG", "Images"),
        ("a.pdf", "Documents"),
        ("a.csv", "Spreadsheets"),
        ("a.pptx", "Presentations"),
        ("a.mp3", "Audio"),
        ("a.mp4", "Video"),
        ("a.zip", "Archives"),
        ("a.py", "Code"),
        ("a.weird", "Other"),
        ("no_extension", "Other"),
    ],
)
def test_categories(name, expected):
    assert category_for(Path(name)) == expected


def test_plan_is_non_destructive(tmp_path):
    source = tmp_path / "photo.jpg"
    source.write_text("picture")
    plan = build_plan(tmp_path)
    assert len(plan) == 1
    assert plan[0].destination == tmp_path / "Images" / "photo.jpg"
    assert source.exists()
    assert not (tmp_path / "Images").exists()


def test_apply_moves_file(tmp_path):
    source = tmp_path / "report.pdf"
    source.write_text("report")
    completed = execute_plan(build_plan(tmp_path))
    assert len(completed) == 1
    assert not source.exists()
    assert (tmp_path / "Documents" / "report.pdf").read_text() == "report"


def test_collision_renamed(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "photo.png").write_text("old")
    (tmp_path / "photo.png").write_text("new")
    plan = build_plan(tmp_path)
    assert plan[0].destination.name == "photo (1).png"
    execute_plan(plan)
    assert (tmp_path / "Images" / "photo.png").read_text() == "old"
    assert (tmp_path / "Images" / "photo (1).png").read_text() == "new"


def test_existing_target_after_planning_fails(tmp_path):
    (tmp_path / "a.txt").write_text("source")
    plan = build_plan(tmp_path)
    plan[0].destination.parent.mkdir()
    plan[0].destination.write_text("existing")
    with pytest.raises(FileExistsError):
        execute_plan(plan)
    assert (tmp_path / "a.txt").exists()
    assert plan[0].destination.read_text() == "existing"


def test_hidden_skipped_by_default(tmp_path):
    (tmp_path / ".secret.txt").write_text("hidden")
    assert build_plan(tmp_path) == []
    assert len(build_plan(tmp_path, include_hidden=True)) == 1


def test_subdirectories_not_organized(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "x.pdf").write_text("x")
    assert build_plan(tmp_path) == []


def test_invalid_directory(tmp_path):
    with pytest.raises(ValueError):
        build_plan(tmp_path / "missing")


def test_cli_preview_then_apply(tmp_path, capsys):
    (tmp_path / "hello.txt").write_text("hello")
    assert main([str(tmp_path)]) == 0
    assert "Preview only" in capsys.readouterr().out
    assert (tmp_path / "hello.txt").exists()
    assert main([str(tmp_path), "--apply"]) == 0
    assert (tmp_path / "Documents" / "hello.txt").exists()


def test_empty_directory(tmp_path, capsys):
    assert main([str(tmp_path)]) == 0
    assert "No eligible files" in capsys.readouterr().out


def test_multiple_same_category(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.md").write_text("b")
    assert len(execute_plan(build_plan(tmp_path))) == 2
    assert (tmp_path / "Documents" / "a.txt").exists()
    assert (tmp_path / "Documents" / "b.md").exists()


def test_second_run_no_changes(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    execute_plan(build_plan(tmp_path))
    assert build_plan(tmp_path) == []
