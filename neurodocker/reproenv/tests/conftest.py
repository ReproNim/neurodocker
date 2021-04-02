import subprocess

import pytest


def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    """Callback to run at the end of all tests."""
    print("removing Docker images made during this testing session")
    # Remove docker images built during tests.
    p = subprocess.run(
        ["docker", "image", "ls", "reproenv-pytest-*", "--quiet"], capture_output=True
    )
    imgs = [img.strip() for img in p.stdout.decode().splitlines()]
    _ = subprocess.run(["docker", "image", "rm", "--force", *imgs])
    _ = subprocess.run(["docker", "builder", "prune", "--force"])
