import build_utils

import pytest


@pytest.mark.parametrize(
    ("product_version", "expected_target"),
    [
        ("10.15.7", "10.15"),
        ("11.7.10", "11.0"),
        ("15.6.1", "15.0"),
        ("26.0", "26.0"),
    ],
)
def test_resolve_macos_deployment_target(product_version, expected_target):
    assert (
        build_utils.resolve_macos_deployment_target(product_version) == expected_target
    )


def test_resolve_macos_deployment_target_rejects_invalid_values():
    with pytest.raises(ValueError, match="Unsupported macOS version string"):
        build_utils.resolve_macos_deployment_target("Tahoe")
