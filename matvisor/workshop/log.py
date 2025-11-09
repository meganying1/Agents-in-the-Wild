import json, time, uuid, threading
from pathlib import Path


class Logger:
    
    def __init__(self, path: str = "log.jsonl"):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.run_id = str(uuid.uuid4())

    def log(self, payload: dict):
        payload = dict(
            run_id=self.run_id,
            ts=time.time(),
            **payload,
        )
        with self._lock:  # safe if multi-threaded
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    log_path = Path("agent_trace_example.jsonl")  # path for the example log
    logger = Logger(path=log_path)  # create a logger instance
    logger.log({"event": "demo", "details": "testing JSONLogger"})  # log a test event
    print(log_path.read_text(encoding="utf-8").strip())  # print the log content
    log_path.unlink(missing_ok=True)  # clean up
