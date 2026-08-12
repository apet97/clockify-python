"""Phase 1 smoke: both packages import."""


def test_packages_import() -> None:
    import clockify
    import clockify_mcp

    assert clockify.__doc__
    assert clockify_mcp.__doc__
