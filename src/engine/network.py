import asyncio
from typing import Dict

from src.agents.router import Router
from src.agents.supervisor import Supervisor
from src.agents.worker import Worker


class Network:
    supervisor: Supervisor
    workers: Dict[int, Worker]
    router: Router

    def __init__(
        self,
        workers: Dict[int, Worker],
        supervisor: Supervisor,
        router: Router,
    ):
        self.workers = workers
        self.supervisor = supervisor
        self.router = router

    def register_worker(self, worker: Worker):
        self.workers.append(worker)

    async def run(self, task: str):
        self.router.route(task)
        async_tasks = [
            self.router.listen(),
            *[worker.listen() for worker in self.workers.values()],
        ]
        task_result = await asyncio.gather(*async_tasks)
        print(task_result)

    def stop(self):
        for worker in self.workers.values():
            worker.running = False
        print("Network stopped.")
