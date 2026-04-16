from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import engine, Base
import models
from controllers import nodes, edges, routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Network Route Optimization API",
    description=(
        "Manage network nodes and edges, compute the shortest latency path "
        "between any two nodes using Dijkstra's algorithm, and browse query history."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": str(exc.detail)})


@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    return JSONResponse(status_code=400, content={"error": str(exc.detail)})


app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(routes.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Network Route Optimization API is running"}
