"""Unit tests for Vics Agent tools."""

import os
import tempfile
from pathlib import Path

import pytest

from vics_agent.tools import execute_tool


@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace for testing."""
    return tmp_path


class TestReadFile:
    def test_read_existing_file(self, workspace):
        (workspace / "hello.txt").write_text("Hello, World!")
        result = execute_tool("read_file", {"path": "hello.txt"}, workspace)
        assert result == "Hello, World!"

    def test_read_nonexistent_file(self, workspace):
        result = execute_tool("read_file", {"path": "nope.txt"}, workspace)
        assert "Error" in result

    def test_read_path_traversal_blocked(self, workspace):
        result = execute_tool("read_file", {"path": "../../etc/passwd"}, workspace)
        assert "Error" in result


class TestWriteFile:
    def test_write_new_file(self, workspace):
        result = execute_tool("write_file", {"path": "test.py", "content": "print('hi')"}, workspace)
        assert "Successfully wrote" in result
        assert (workspace / "test.py").read_text() == "print('hi')"

    def test_write_creates_directories(self, workspace):
        result = execute_tool(
            "write_file",
            {"path": "src/utils/helpers.py", "content": "# helpers"},
            workspace,
        )
        assert "Successfully wrote" in result
        assert (workspace / "src" / "utils" / "helpers.py").exists()

    def test_write_path_traversal_blocked(self, workspace):
        result = execute_tool(
            "write_file",
            {"path": "../../../tmp/evil.sh", "content": "rm -rf /"},
            workspace,
        )
        assert "Error" in result


class TestEditFile:
    def test_edit_replaces_string(self, workspace):
        (workspace / "app.py").write_text("name = 'old'\nprint(name)")
        result = execute_tool(
            "edit_file",
            {"path": "app.py", "old_string": "name = 'old'", "new_string": "name = 'new'"},
            workspace,
        )
        assert "Successfully edited" in result
        assert "name = 'new'" in (workspace / "app.py").read_text()

    def test_edit_fails_if_not_found(self, workspace):
        (workspace / "app.py").write_text("hello")
        result = execute_tool(
            "edit_file",
            {"path": "app.py", "old_string": "nonexistent", "new_string": "replacement"},
            workspace,
        )
        assert "not found" in result

    def test_edit_fails_if_ambiguous(self, workspace):
        (workspace / "app.py").write_text("x = 1\nx = 1\n")
        result = execute_tool(
            "edit_file",
            {"path": "app.py", "old_string": "x = 1", "new_string": "x = 2"},
            workspace,
        )
        assert "2 times" in result


class TestListDirectory:
    def test_list_directory(self, workspace):
        (workspace / "file.txt").write_text("content")
        (workspace / "subdir").mkdir()
        result = execute_tool("list_directory", {"path": "."}, workspace)
        assert "file.txt" in result
        assert "subdir/" in result

    def test_list_empty_directory(self, workspace):
        (workspace / "empty").mkdir()
        result = execute_tool("list_directory", {"path": "empty"}, workspace)
        assert "empty" in result.lower()


class TestSearchFiles:
    def test_search_finds_pattern(self, workspace):
        (workspace / "main.py").write_text("def hello():\n    return 'world'")
        result = execute_tool("search_files", {"pattern": "hello"}, workspace)
        assert "main.py" in result
        assert "hello" in result

    def test_search_no_matches(self, workspace):
        (workspace / "main.py").write_text("print('hi')")
        result = execute_tool("search_files", {"pattern": "nonexistent_xyz"}, workspace)
        assert "No matches" in result


class TestRunCommand:
    def test_run_echo(self, workspace):
        result = execute_tool("run_command", {"command": "echo hello"}, workspace)
        assert "hello" in result

    def test_run_blocked_command(self, workspace):
        result = execute_tool("run_command", {"command": "rm -rf /"}, workspace)
        assert "blocked" in result.lower()

    def test_run_timeout(self, workspace):
        # Use a very short timeout
        if os.name == "nt":
            cmd = "ping -n 10 127.0.0.1"
        else:
            cmd = "sleep 10"
        result = execute_tool("run_command", {"command": cmd, "timeout": 1}, workspace)
        assert "timed out" in result.lower()


class TestDeleteFile:
    def test_delete_existing(self, workspace):
        (workspace / "temp.txt").write_text("delete me")
        result = execute_tool("delete_file", {"path": "temp.txt"}, workspace)
        assert "Deleted" in result
        assert not (workspace / "temp.txt").exists()

    def test_delete_nonexistent(self, workspace):
        result = execute_tool("delete_file", {"path": "nope.txt"}, workspace)
        assert "Error" in result


class TestUnknownTool:
    def test_unknown_tool(self, workspace):
        result = execute_tool("nonexistent_tool", {}, workspace)
        assert "Unknown tool" in result
