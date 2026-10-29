"""API server entry point.

    uvicorn apps.api.main:app --host 0.0.0.0 --port 8000

or, equivalently, ``argus start``. Run a single worker: the sensor pipeline
lives in the API process (see docs/architecture.md).
"""

from argus.api.app import create_app

app = create_app()
