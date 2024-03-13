from typing import Dict, List

from src.agents.worker import Worker


def workers_to_map(workers: List[Worker]) -> Dict[int, Worker]:
    workers_mapping = {}
    for worker in workers:
        workers_mapping[worker.id] = worker
    return workers_mapping
