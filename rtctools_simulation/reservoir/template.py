"""Module for creating a template for a reservoir model."""
import logging
from distutils.dir_util import copy_tree
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("rtctools")

SOURCE_DIR = Path(__file__).parent.resolve() / "template_data"
DESTINATION_DIR = Path(__file__).parent.parent.parent.resolve() / "tests" / "reservoir_template"


def convert_to_camel_case(name: str):
    """Convert a string to camel case."""
    name = name.title()
    name = "".join(filter(str.isalnum, name))
    return name


def render_reservoir_file(template_file: Path, reservoir_name: str):
    """Render a reservoir template file."""
    template_file = Path(template_file).resolve()
    py_file = template_file.with_suffix(".py")
    environment = Environment(
        loader=FileSystemLoader(template_file.parent),
        keep_trailing_newline=True,
    )
    template = environment.get_template(template_file.name)
    reservoir_name = convert_to_camel_case(reservoir_name)
    content = template.render(reservoir_name=reservoir_name)
    with open(py_file, mode="w") as file:
        file.write(content)


def create_reservoir_dir(dir: Path, reservoir_name: str, allow_overwrite: bool = False):
    """Create a directory with template files for a reservoir model."""
    dir = Path(dir)
    if dir.is_dir() and not allow_overwrite:
        raise ValueError(
            f"Directory {dir} already exists."
            " Use the -f option to overwrite an existing directory."
        )
    dir.mkdir(parents=True, exist_ok=True)
    copy_tree(str(SOURCE_DIR), str(dir))
    template_file = dir / "reservoir.txt"
    render_reservoir_file(template_file, reservoir_name=reservoir_name)
    template_file.unlink()
