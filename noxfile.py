"""Nox sessions."""

import sys
from pathlib import Path

import nox
from nox_poetry import Session, session


package = "galas"
python_versions = ["3.11"]
nox.options.sessions = (
    "mypy",
    "ruff",
    "safety",
    "tests",
    "typeguard",
)
locations_without_noxfile = ["src", "tests"]  # docs/conf.py
locations = locations_without_noxfile + ["noxfile.py"]


@session(python=python_versions[0])
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@session(python=python_versions[0])
def coverage(session: Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report"]
    session.install("coverage[toml]")
    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")
    session.run("coverage", *args)


@session(python=python_versions[0])
def isort(session: Session) -> None:
    """Sort imports using isort."""
    args = session.posargs or locations
    session.install("isort")
    session.run("isort", *args)


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Static type-checking using mypy."""
    args = session.posargs or locations_without_noxfile
    session.install(".")
    session.install("mypy", "types-python-dateutil")
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python=python_versions)
def ruff(session: Session) -> None:
    """Lint code using ruff."""
    args = session.posargs or locations
    session.install("ruff")
    session.run("ruff", *args)


@session(python=python_versions[0])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run("safety", "check", "--full-report", f"--file={requirements}")


@session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    session.install(".")
    session.install("pytest", "freezegun", "coverage[toml]")  # pygments?
    session.run("coverage", "run", "--parallel", "-m", "pytest", *session.posargs)

    # TODO: if session.interactive?
    session.notify("coverage", posargs=[])


@session(python=python_versions)
def typeguard(session: Session) -> None:
    """Dynamic type checking using Typeguard."""
    session.install(".")
    session.install("pytest", "freezegun", "typeguard")  # pygments?
    session.run("pytest", f"--typeguard-packages={package}", *session.posargs)
