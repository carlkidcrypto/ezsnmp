from configparser import ConfigParser
from pathlib import Path


def test_build_requirements_are_declared_only_in_pyproject():
    config = ConfigParser()
    config.read_string(
        (Path(__file__).resolve().parents[1] / "setup.cfg").read_text(encoding="utf-8")
    )

    assert not config.has_option("options", "setup_requires"), (
        "Declare build requirements only in pyproject.toml [build-system].requires; "
        "setup_requires can conflict with the isolated build environment."
    )
