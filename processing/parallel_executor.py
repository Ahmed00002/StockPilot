# processing/parallel_executor.py
import concurrent.futures
import threading

class ParallelExecutor:
    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()

    def run_parallel(self, func, items):
        futures = []
        for item in items:
            futures.append(self.executor.submit(func, item))
        return [f.result() for f in concurrent.futures.as_completed(futures)]

    def shutdown(self):
        self.executor.shutdown(wait=True)