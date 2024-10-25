import asyncio
import json
import logging
import sys
from threading import Lock
from typing import AsyncGenerator, List, Optional

from fastapi import BackgroundTasks, FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from autobox.api.abort_simulation import handle_abort_simulation
from autobox.api.create_server_simulation import handle_create_server_simulation
from autobox.api.get_metrics_by_simulation_id import handle_get_metrics_by_simulation_id
from autobox.api.get_organizations import handle_get_organizations
from autobox.api.get_projects import handle_get_projects
from autobox.api.get_prometheus_metrics import handle_prometheus_metrics
from autobox.api.get_simulation_by_id import handle_get_simulation_by_id
from autobox.api.get_simulations import handle_get_simulations
from autobox.api.ping import handle_ping
from autobox.api.update_agent_instruction import handle_update_simulation_instruction
from autobox.cache.cache import Cache
from autobox.common.logger import Logger
from autobox.core.simulation import Simulation
from autobox.schemas.config import ServerConfig
from autobox.schemas.metrics import MetricResponse
from autobox.schemas.simulation import (
    InstructionRequest,
    SimulationRequest,
    SimulationResponse,
)

progress_lock = Lock()


class ExcludeEndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            "/metrics" not in record.getMessage()
            and "?streaming=true" not in record.getMessage()
        )


def create_app():
    app = FastAPI()
    logger = Logger.get_instance()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(ExcludeEndpointFilter())

    @app.get("/ping")
    async def ping():
        logger.info("Ping received.")
        return handle_ping()

    async def progress_stream(simulation_id: str) -> AsyncGenerator[str, None]:
        try:
            while True:
                simulation = await handle_get_simulation_by_id(simulation_id)
                yield f"data: {json.dumps(simulation.model_dump(), default=str)}\n\n"
                await asyncio.sleep(1)
                if simulation.progress >= 100 or simulation.status != "in progress":
                    break
        except Exception as e:
            yield f"data: {{'error': 'An error occurred: {str(e)}'}}\n\n"

    async def traces_stream(
        simulation: Simulation, traces: List[str]
    ) -> AsyncGenerator[str, None]:
        try:
            while True:
                data = {
                    "traces": traces,
                    "progress": simulation.progress,
                    "status": simulation.status,
                }
                yield f"data: {json.dumps(data, default=str)}\n\n"
                await asyncio.sleep(1)
                if simulation.progress >= 100 or simulation.status != "in progress":
                    break
        except Exception as e:
            yield f"data: {{'error': 'An error occurred: {str(e)}'}}\n\n"

    @app.get("/simulations", response_model=List[SimulationResponse])
    async def get_simulations():
        return await handle_get_simulations()

    @app.get("/simulations/{simulation_id}", response_model=SimulationResponse)
    async def get_simulation_by_id(
        simulation_id: str, streaming: Optional[bool] = Query(False)
    ):
        if streaming:
            return StreamingResponse(
                progress_stream(simulation_id), media_type="text/event-stream"
            )
        return await handle_get_simulation_by_id(simulation_id)

    @app.get("/simulations/{simulation_id}/traces", response_model=List[str])
    async def get_simulation_traces_by_id(
        simulation_id: str, streaming: Optional[bool] = Query(False)
    ):
        simulation = await handle_get_simulation_by_id(simulation_id)
        traces = Cache.traces().get_traces_by(simulation_id)
        if streaming and simulation.status == "in progress":
            return StreamingResponse(
                traces_stream(simulation, traces), media_type="text/event-stream"
            )
        return traces

    @app.get(
        "/simulations/{simulation_id}/metrics", response_model=List[MetricResponse]
    )
    async def get_metrics_by_simulation_id(simulation_id: str):
        return await handle_get_metrics_by_simulation_id(simulation_id)

    @app.post("/simulations/{simulation_id}/abort")
    async def abort_simulation(simulation_id: str):
        return await handle_abort_simulation(simulation_id)

    @app.post("/simulations/{simulation_id}/agents/{agent_id}/instruction")
    async def update_simulation_instruction(
        simulation_id: str,
        agent_id: str,
        request: InstructionRequest,
        response: Response,
    ):
        return await handle_update_simulation_instruction(
            simulation_id, agent_id, request, response
        )

    @app.post("/simulations")
    async def post_simulations(
        request: SimulationRequest,
        background_tasks: BackgroundTasks,
        response: Response,
    ):
        return await handle_create_server_simulation(
            request, background_tasks, response
        )

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Server is shutting down...")

    @app.get("/metrics")
    async def prometheus_metrics():
        return handle_prometheus_metrics()

    @app.get("/projects")
    async def get_projects():
        return await handle_get_projects()

    @app.get("/organizations")
    async def get_organizations():
        return await handle_get_organizations()

    return app


def start_server(config: ServerConfig):
    import uvicorn

    logger = Logger.get_instance()
    logger.info("Starting Autobox server...")

    try:
        uvicorn.run(
            "autobox.server:create_app",  # Pass the app factory as an import string
            host=config.host,
            port=config.port,
            reload=config.reload,  # Use reload only in development mode
            factory=True,  # Enable factory mode to use create_app
        )
    except Exception as e:
        logger.error(f"Server encountered an error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Autobox server has stopped.")
