"""Module for setting up a simulation configuration."""
from pathlib import Path
from typing import Dict, List


class ModelConfig:
    """Class that describes a simulation configuration."""

    def __init__(
        self,
        model: str,
        base_dir: Path = None,
        dirs: Dict[str, Path] = None,
        files: Dict[str, Path] = None,
    ):
        self.model = model
        self.base_dir = base_dir
        self._dirs = dirs if dirs is not None else {}
        self.resolve_dirs()
        self._files = files if files is not None else {}
        self.resolve_files()

    def get_dir(self, dir_name: str) -> Path:
        """Get a directory."""
        if dir_name in self._dirs:
            dir = self._dirs[dir_name]
            dir = Path(dir).resolve()
        elif self.base_dir is not None:
            dir = self.base_dir / dir_name
            dir = Path(dir).resolve()
            if not dir.is_dir():
                dir = self.base_dir
                dir = Path(dir).resolve()
        if not dir.is_dir():
            raise ValueError(f"Directory {dir_name} not found.")
        return dir

    def get_file(self, file_name: str, dirs: List[str] = None, default: Path = None) -> Path:
        """Get a file."""
        if file_name in self._files:
            file = self._files[file_name]
            file = Path(file).resolve()
        elif self.base_dir is not None:
            file = self.base_dir / file_name
            file = Path(file).resolve()
        if not file.is_file() and dirs is not None:
            # Search in given list of directories.
            for dir_name in dirs:
                dir = self.get_dir(dir_name)
                file = dir / file_name
                file = Path(file).resolve()
                if file.is_file():
                    break
        if not file.is_file():
            if default is not None:
                return default
            raise ValueError(f"File {file_name} not found.")
        return file

    def resolve_dirs(self):
        """Resolve directories."""
        if self.base_dir is not None:
            self.base_dir = Path(self.base_dir).resolve()
            assert self.base_dir.is_dir()
        for dir_name in self._dirs:
            self._dirs[dir_name] = self.get_dir(dir_name)

    def resolve_files(self):
        """Resolve files."""
        for file_name in self._files:
            self._files[file_name] = self.get_file(file_name)
