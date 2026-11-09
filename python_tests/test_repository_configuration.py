from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_sonarcloud_configuration() -> None:
    sonar_path = REPO_ROOT / ".sonarcloud.properties"
    assert sonar_path.is_file(), ".sonarcloud.properties must exist"
    content = sonar_path.read_text(encoding="utf-8")
    assert "sonar.sources" in content
    assert "sonar.tests" in content
    assert "sonar.python.version" in content
    assert "sonar.exclusions" in content
    assert "sonar.cpd.exclusions" in content
    assert "docs/**" in content
    assert ".github/**" in content
    assert "third_party/**" in content
    assert "python_tests/**" in content
    assert "cpp_tests/**" in content
    assert "integration_tests/**" in content


def test_codecov_configuration() -> None:
    codecov_path = REPO_ROOT / "codecov.yml"
    assert codecov_path.is_file(), "codecov.yml must exist"
    content = codecov_path.read_text(encoding="utf-8")
    assert "codecov" in content
