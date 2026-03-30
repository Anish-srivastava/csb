"""
Real-time ransomware behavior monitor (Educational).

What it does:
- Watches only test_folder
- Logs file modifications, renames, and alerts
- Uses rule-based + ML classification
"""

from collections import deque
from datetime import datetime
import json
from pathlib import Path
import time

import joblib
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FOLDER = BASE_DIR / "test_folder"
LOG_FILE = BASE_DIR / "logs" / "activity_log.txt"
STATS_FILE = BASE_DIR / "logs" / "stats.json"
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"

WINDOW_SECONDS = 10
RAPID_CHANGE_THRESHOLD = 5


class RansomwareMonitor(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.event_times = deque()
        self.extension_change_times = deque()
        self.model = self.load_model()
        self.stats = self.load_stats()
        self.ensure_log_header()

    def load_model(self):
        if MODEL_PATH.exists():
            return joblib.load(MODEL_PATH)
        return None

    def load_stats(self):
        if STATS_FILE.exists():
            try:
                return json.loads(STATS_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"total_files_scanned": 0, "suspicious_activity_count": 0}

    def save_stats(self):
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATS_FILE.write_text(json.dumps(self.stats, indent=2), encoding="utf-8")

    def ensure_log_header(self):
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
            LOG_FILE.write_text(
                "timestamp|event|path|classification|message\n",
                encoding="utf-8",
            )

    def write_log(self, event: str, path: Path, classification: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp}|{event}|{path}|{classification}|{message}\n"
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(line)

    def classify_behavior(self, file_change_rate: float, extension_change_count: int) -> str:
        if self.model is not None:
            prediction = self.model.predict([[file_change_rate, extension_change_count]])[0]
            return "Ransomware" if int(prediction) == 1 else "Normal"

        # Fallback heuristic if model is missing.
        if file_change_rate > 5 and extension_change_count > 2:
            return "Ransomware"
        return "Normal"

    def update_window(self, is_extension_change: bool = False):
        now = time.time()
        self.event_times.append(now)
        if is_extension_change:
            self.extension_change_times.append(now)

        while self.event_times and (now - self.event_times[0]) > WINDOW_SECONDS:
            self.event_times.popleft()
        while self.extension_change_times and (now - self.extension_change_times[0]) > WINDOW_SECONDS:
            self.extension_change_times.popleft()

    def evaluate_activity(self, path: Path, trigger_event: str):
        file_change_rate = len(self.event_times)
        extension_change_count = len(self.extension_change_times)
        classification = self.classify_behavior(file_change_rate, extension_change_count)

        self.stats["total_files_scanned"] += 1

        alert_message = "Monitoring"
        if file_change_rate > RAPID_CHANGE_THRESHOLD:
            classification = "Ransomware"
            alert_message = "Rapid file changes detected"
            print("⚠ Ransomware Detected!")

        if classification == "Ransomware":
            self.stats["suspicious_activity_count"] += 1

        self.write_log(
            event=trigger_event,
            path=path,
            classification=classification,
            message=f"rate={file_change_rate}, ext_changes={extension_change_count}, note={alert_message}",
        )
        self.save_stats()

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        self.update_window(is_extension_change=path.suffix == ".locked")
        self.evaluate_activity(path, "modified")

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        self.update_window(is_extension_change=path.suffix == ".locked")
        self.evaluate_activity(path, "created")

    def on_moved(self, event):
        if event.is_directory:
            return
        destination = Path(event.dest_path)
        src = Path(event.src_path)
        extension_changed = src.suffix != destination.suffix or destination.suffix == ".locked"
        self.update_window(is_extension_change=extension_changed)
        self.evaluate_activity(destination, "renamed")


def start_monitor():
    if not TEST_FOLDER.exists():
        print(f"test_folder not found: {TEST_FOLDER}")
        return

    event_handler = RansomwareMonitor()
    observer = Observer()
    observer.schedule(event_handler, str(TEST_FOLDER), recursive=True)

    print(f"Monitoring started on: {TEST_FOLDER}")
    print("Press Ctrl+C to stop")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_monitor()
