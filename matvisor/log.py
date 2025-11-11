import json
import uuid
import threading
from pathlib import Path


class Logger:
    """
    JSONL logger with:
      - per-instance run_id (UUID)  # Not needed anymore
      - per-file globally incremental id starting from 0
      - safe for multiple Logger instances & threads in the same process
    """

    # Shared across all Logger instances (per process)
    _global_lock = threading.Lock()
    _file_locks = {}      # path -> threading.Lock()
    _next_ids = {}        # path -> int (next id to use)

    def __init__(self, path: str = "log.jsonl"):
        self.path = Path(path)
        self.run_id = str(uuid.uuid4())

        # Ensure directory exists
        if self.path.parent:
            self.path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure per-file lock and id counter are initialized once
        with Logger._global_lock:
            # Create a lock for this file path if not present
            if self.path not in Logger._file_locks:
                Logger._file_locks[self.path] = threading.Lock()

            # Initialize the next id for this file if not present
            if self.path not in Logger._next_ids:
                # Lock the file while we inspect existing contents
                # to avoid races with other threads in this process.
                file_lock = Logger._file_locks[self.path]
                with file_lock:
                    Logger._next_ids[self.path] = self._compute_initial_next_id()

    def _compute_initial_next_id(self) -> int:
        """
        Scan the existing log file (if any) and find the last used `id`.
        Returns the next id to use. Starts from 0 if no valid id is found.
        """
        if not self.path.exists():
            return 0

        last_id = -1

        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Backward compatible: only care if id exists and is int-like
                _id = obj.get("id")
                if isinstance(_id, int) and _id > last_id:
                    last_id = _id

        # If no id found, start at 0; else continue from last_id + 1
        return last_id + 1 if last_id >= 0 else 0

    def _get_next_id(self) -> int:
        """
        Atomically fetch & increment the global counter for this file (per process).
        """
        with Logger._global_lock:
            next_id = Logger._next_ids[self.path]
            Logger._next_ids[self.path] += 1
            return next_id

    def log(self, payload: dict):
        """
        Append a JSON line with:
          - global incremental `id` per file
          - per-instance `run_id`  # Not needed anymore
          - user payload fields
        Thread-safe across instances in this process.
        """
        entry_id = self._get_next_id()

        record = dict(
            id=entry_id,
            #run_id=self.run_id,
            **payload,
        )

        file_lock = Logger._file_locks[self.path]
        line = json.dumps(record, ensure_ascii=False)

        # Only one writer per file at a time (within this process)
        with file_lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")


if __name__ == "__main__":
    log_path = Path("agent_trace_example.jsonl")
    logger1 = Logger(path=log_path)
    logger2 = Logger(path=log_path)

    logger1.log({"event": "demo", "details": "from logger1"})
    logger2.log({"event": "demo", "details": "from logger2"})
    logger1.log({"event": "demo", "details": "again from logger1"})

    print(log_path.read_text(encoding="utf-8").strip())
    log_path.unlink(missing_ok=True)