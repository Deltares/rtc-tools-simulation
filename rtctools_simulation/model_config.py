"""Module for setting up a simulation configuration."""
from pathlib import Path
from typing import Dict, List


class ModelConfig:
    """
    Class that describes a simulation configuration.

    In particular, this class describes the name of the Modelica model
    and where to find the input and output files for running the model.

    A typical file structure for model input and output looks as follows.

    <base_dir>
    ├───...
    ├───input
    │   ├───rtcDataConfig.xml
    │   ├───rtcParameterConfig.xml
    │   ├───timeseries_import.xml
    │   └───...
    ├───lookup_tables
    │   ├───lookup_tables.csv
    │   └───...
    ├───model
    │   ├───lookup_table_equations.csv
    │   └───...
    └───output
        └───...

    The <base_dir> directory can be set by the parameter base_dir.
    Paths to specific files and folders can be set with the files and dirs parameters.
    Consider, for example, the following configuration.

    ModelConfig(
        base_dir="path/to/my/base_dir",
        dirs={"output": "path/to/my/output_dir"},
        files={"lookup_tables.csv": "path/to/my/lookup_tables.csv"}
    )

    This configuration will search for the output folder in "path/to/my/output_dir"
    and for the lookup_tables.csv file in "path/to/my/lookup_tables.csv".
    For any other file and folder, it will search according to the above file structure.
    So for the timeseries_import.xml file it will look for
    "path/to/my/base_dir/input/timeseries_import.xml".
    """

    def __init__(
        self,
        model: str = None,
        base_dir: Path = None,
        dirs: Dict[str, Path] = None,
        files: Dict[str, Path] = None,
    ):
        self._model = None
        self._base_dir = None
        self._dirs = {}
        self._files = {}
        self.set_model(model)
        self.set_base_dir(base_dir)
        self.set_dirs(dirs)
        self.set_files(files)

    def model(self) -> str:
        """Get the model name"""
        return self._model

    def base_dir(self) -> Path:
        """Get the base directory."""
        return self._base_dir

    def dirs(self) -> Dict[str, Path]:
        """Get a dict of directories."""
        return self._dirs

    def files(self) -> Dict[str, Path]:
        """Get a dict of files."""
        return self._files

    def set_model(self, model: str):
        """Set the model name."""
        self._model = model

    def set_base_dir(self, base_dir: Path):
        """Set the base directory."""
        if base_dir is not None:
            base_dir = Path(base_dir).resolve()
            assert base_dir.is_dir()
        self._base_dir = base_dir

    def set_dir(self, dir_name: str, dir: Path):
        """Set a directory."""
        dir = Path(dir).resolve()
        assert dir.is_dir(), f"Directory {dir} not found."
        self._dirs[dir_name] = dir

    def set_file(self, file_name: str, file: Path):
        """Set a file."""
        file = Path(file).resolve()
        assert file.is_file(), f"File {file} not found."
        self._files[file_name] = file

    def set_dirs(self, dirs: Dict[str, Path]):
        """Set directories."""
        if dirs is None:
            dirs = {}
        for dir_name, dir in dirs.items():
            self.set_dir(dir_name, dir)

    def set_files(self, files: Dict[str, Path]):
        """Set files."""
        if files is None:
            files = {}
        for file_name, file in files.items():
            self.set_file(file_name, file)

    def get_dir(self, dir_name: str) -> Path:
        """
        Get a directory.

        Returns None if the directory is not found.
        """
        dir = None
        if dir_name in self._dirs:
            dir = self._dirs[dir_name]
        elif self._base_dir is not None:
            dir = self._base_dir / dir_name
        return dir if dir is not None and dir.is_dir() else None

    def get_file(self, file_name: str, dirs: List[str] = None) -> Path:
        """
        Get a file.

        Returns None if the file is not found.
        """
        file = None
        if file_name in self._files:
            file = self._files[file_name]
        elif dirs is not None:
            # Search in given list of directories.
            for dir_name in dirs:
                dir = self.get_dir(dir_name)
                if dir is None:
                    continue
                file = dir / file_name
                if file.is_file():
                    break
        return file if file is not None and file.is_file() else None
