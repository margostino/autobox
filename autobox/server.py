import logging
import sys
from typing import List

from fastapi import BackgroundTasks, FastAPI, Response

from autobox.api.abort_simulation import handle_abort_simulation
from autobox.api.create_simulation import handle_create_simulation
from autobox.api.get_metrics_by_simulation_id import handle_get_metrics_by_simulation_id
from autobox.api.get_prometheus_metrics import handle_prometheus_metrics
from autobox.api.get_simulation_by_id import handle_get_simulation_by_id
from autobox.api.get_simulations import handle_get_simulations
from autobox.api.ping import handle_ping
from autobox.api.update_agent_instruction import handle_update_simulation_instruction
from autobox.common.logger import Logger
from autobox.schemas.config import ServerConfig
from autobox.schemas.metrics import MetricsResponse
from autobox.schemas.simulation import (
    InstructionRequest,
    SimulationRequest,
    SimulationStatusResponse,
)


class ExcludeEndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/metrics" not in record.getMessage()


def create_app():
    app = FastAPI()
    logger = Logger.get_instance()

    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(ExcludeEndpointFilter())

    @app.get("/ping")
    async def ping():
        logger.info("Ping received.")
        return handle_ping()

    @app.get("/simulations", response_model=List[SimulationStatusResponse])
    async def get_simulations():
        return await handle_get_simulations()

    @app.get("/simulations/{simulation_id}", response_model=SimulationStatusResponse)
    async def get_simulation_by_id(simulation_id: str):
        return await handle_get_simulation_by_id(simulation_id)

    @app.get("/simulations/{simulation_id}/metrics", response_model=MetricsResponse)
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
        return await handle_create_simulation(request, background_tasks, response)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Server is shutting down...")

    @app.get("/metrics")
    async def prometheus_metrics():
        return handle_prometheus_metrics()

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
