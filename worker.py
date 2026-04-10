import os
import redis
from rq import Worker, Queue

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    queues = [Queue(connection=conn)]
    worker = Worker(queues, connection=conn)
    worker.work()
