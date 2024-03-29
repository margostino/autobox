import asyncio
from typing import Dict

from engine.messaging import Message
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
        start_message = Message(task)
        self.router.mailbox.put_nowait(start_message)
        async_tasks = [
            self.router.listen(),
            *[worker.listen() for worker in self.workers.values()],
        ]
        await asyncio.gather(*async_tasks)
        output = self.router.memory[-1]  # TODO: define how to get final output
        print(f"Output: {output}")

    def stop(self):
        self.router.stop()
        for worker in self.workers.values():
            worker.running = False
        print("[Network] network stopped.")
