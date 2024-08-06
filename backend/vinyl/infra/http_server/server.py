from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, Query, Request
from vinyl.lib.project import Project
from vinyl.lib.query_engine import QueryEngine


class ProjectDependency:
    def __init__(self, project: Project):
        self.project = project


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load project on startup
    app.state.project = Project.bootstrap()
    yield
    # clean up here
    pass


def get_project(request: Request) -> Project:
    return request.app.state.project


# Create an instance of the FastAPI class
app = FastAPI(lifespan=lifespan)


# Define a route at the root '/'
@app.get("/")
async def _root():
    return {"status": "OK"}


@app.get("/models/{name}")
async def _get_model(
    name: str,
    limit: int = 1000,
    project: ProjectDependency = Depends(get_project),
):
    query_engine = QueryEngine(project)
    result = query_engine._model(name, limit)
    return {"limit": limit, "rows": result.to_records()}


@app.get("/metrics/{name}")
async def _get_metrics(
    name: str,
    grain: str,
    metrics: List[str] = Query([]),
    dimensions: List[str] = Query([]),
    limit: int = 1000,
    project: ProjectDependency = Depends(get_project),
):
    """
    Fetch metrics based on the metric name, time granularity, and dimensions

    Args:
    - metric_name (str): The name of the metric.
    - time_grain (str): The granularity of time (e.g., hourly, ex: days=14).
    - dimensions (List[str]): An array of dimensions to filter the metrics.

    Returns:
    - dict: A pandas records with the query parameters received.
    """
    query_engine = QueryEngine(project)
    result = query_engine._metric(store=name, grain=grain, limit=limit)
    return {
        "limit": limit,
        "rows": result.to_records(),
    }
