import math
from datetime import datetime


def calculate_progress(started_at: datetime, timeout: float, iterations: int) -> float:
    current_time = datetime.now()

    # Calculate the elapsed time in seconds since the job started
    elapsed_time = (current_time - started_at).total_seconds()

    # Cap progress at a maximum determined by the timeout
    if elapsed_time >= timeout:
        return 99  # Return a maximum of 99%, allowing 100 to be set elsewhere

    # Control how fast the progress slows down; higher values make it slow faster
    alpha = 5

    # Exponential decay calculation, the closer we get to timeout, the slower progress increases
    progress = (1 - math.exp(-alpha * (elapsed_time / timeout))) * 99  # Capped at 99%

    # Optionally adjust with iterations (e.g., adding or reducing the progress based on iterations)
    adjusted_progress = min(progress + iterations, 99)  # Ensure it never exceeds 99%

    return round(adjusted_progress)
