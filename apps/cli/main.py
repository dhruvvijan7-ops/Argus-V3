"""CLI entry point. Installed as the ``argus`` command; this file allows
``python apps/cli/main.py`` from a source checkout."""

from argus.cli.main import app

if __name__ == "__main__":
    app()
