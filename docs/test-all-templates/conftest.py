from neurodocker.reproenv.state import registered_templates


def pytest_configure(config):
    # register a marker for each template
    for tmpl_name in registered_templates():
        config.addinivalue_line(
            "markers",
            f"template_{tmpl_name}: run tests that build {tmpl_name}",
        )

    config.addinivalue_line(
        "markers", "method_binaries: run tests that use binaries method"
    )
    config.addinivalue_line(
        "markers", "method_source: run tests that use source method"
    )
    config.addinivalue_line(
        "markers", "pkg_manager_apt: run tests that use the apt package manager"
    )
    config.addinivalue_line(
        "markers", "pkg_manager_yum: run tests that use the yum package manager"
    )
