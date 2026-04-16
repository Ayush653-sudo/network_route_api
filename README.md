# Network Route Optimization API

This service exposes a simple REST API for working with a network of nodes and directed connections. It lets you calculate the shortest route between two points based on latency, and keeps a record of previous route queries for later lookup.

At its core, the API builds a graph from your nodes and edges, then applies Dijkstra’s algorithm to determine the lowest-latency path between a source and destination.

## What you can do

You can create and manage nodes identified by unique names, connect them with directed edges that carry a positive latency value, and compute routes between any two nodes. Every successful route lookup is stored so you can revisit or filter past queries.

Data is stored locally using SQLite, and the database schema is set up automatically when the application starts.

## Stack

* FastAPI for building the API
* Uvicorn as the ASGI server
* SQLAlchemy (2.x) for database interaction
* Pydantic (v2) for request and response validation

## Requirements

* Python 3.10 or newer (3.11+ is ideal)
* pip or any compatible package manager

## Setup

Clone the project and create a virtual environment:

```bash
cd network_route_api
python -m venv .venv
```

Activate the environment and install dependencies:

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the app

Start the server from the project root:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Once running:

* Base URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

A quick health check:

```http
GET /
```

## Endpoints overview

* `GET /` — basic health check
* `POST /nodes` — add a node
* `GET /nodes` — list all nodes
* `DELETE /nodes/{node_id}` — remove a node
* `POST /edges` — add a directed edge with latency
* `GET /edges` — list all edges
* `DELETE /edges/{edge_id}` — remove an edge
* `POST /routes/shortest` — compute shortest path and store it
* `GET /routes/history` — fetch past route queries

## Example requests

Create a node:

```json
{ "name": "dc-east" }
```

Create an edge:

```json
{
  "source": "dc-east",
  "destination": "dc-central",
  "latency": 15.0
}
```

Find the shortest route:

```json
{
  "source": "dc-east",
  "destination": "dc-west"
}
```

Latency must always be greater than zero, and both nodes must already exist.

## Filtering route history

You can filter stored routes using query parameters like:

* `source`
* `destination`
* `limit`
* `date_from`
* `date_to`

Example:

```http
GET /routes/history?source=dc-east&limit=10
```

## Status codes

* 200 — successful request
* 201 — resource created
* 204 — resource deleted
* 400 — invalid input or constraint issue
* 404 — no route found

Errors come back as JSON:

```json
{ "error": "message" }
```

## Trying it out

The easiest way is through Swagger:

1. Run the server
2. Open `/docs`
3. Use “Try it out” on any endpoint

You can also use curl or PowerShell to test flows like:

* creating nodes
* linking them with edges
* computing a route
* checking the stored history

## Example scenario

Create a small network:

* Nodes: `dc-east`, `dc-central`, `dc-west`, `edge-pop`
* Edges:

  * dc-east → dc-central (15)
  * dc-central → dc-west (20) → total 35
  * dc-east → edge-pop (8)
  * edge-pop → dc-west (35) → total 43

When you request a route from `dc-east` to `dc-west`, the API should return the shorter path through `dc-central` with a total latency of 35.

## Project structure

```
network_route_api/
├── main.py
├── database.py
├── constants/
├── controllers/
├── models/
├── schemas/
├── services/graph.py
├── requirements.txt
└── README.md
```

A SQLite file (`network_routes.db`) is created automatically on first run.
