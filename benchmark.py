import time
import threading
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

def dummy_task():
    time.sleep(0.01)

def test_threads():
    start = time.time()
    threads = []
    for _ in range(12):
        t = threading.Thread(target=dummy_task)
        t.start()
        threads.append(t)
    return time.time() - start

def test_pool():
    start = time.time()
    for _ in range(12):
        executor.submit(dummy_task)
    return time.time() - start

# warmup
test_threads()
test_pool()

t_threads = sum(test_threads() for _ in range(100)) / 100
t_pool = sum(test_pool() for _ in range(100)) / 100

print(f"Average Thread Spawn Time: {t_threads:.5f} s")
print(f"Average Pool Submit Time:  {t_pool:.5f} s")
