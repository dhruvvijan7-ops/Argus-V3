"""Argus - an explainable network intrusion detection and prevention platform.

The security core (``argus.capture`` through ``argus.response``) is a plain
Python library with no dependency on the web application.  ``argus.api`` and
``argus.cli`` are two front-ends over the same :mod:`argus.pipeline`.
"""

__version__ = "3.0.0"
__all__ = ["__version__"]
