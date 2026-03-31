"""Monitor ../test_folder for ransomware-like behavior and log all events."""

from collections import deque
from datetime import datetime
import json
from pathlib import Path
import time

from watchdog.events import FileSystemEvent, FileSystemEventHandler, FileMovedEvent
from watchdog.observers import Observer

DETECTOR_DIR = Path(__file__).resolve().parent
TEST_FOLDER = (DETECTOR_DIR / "../test_folder").resolve()
LOG_FILE = (DETECTOR_DIR / "../logs/activity_log.txt").resolve()
STATS_FILE = (DETECTOR_DIR / "../logs/stats.json").resolve()

WINDOW_SECONDS = 10
RAPID_CHANGE_THRESHOLD = 5


def ensure_log_files() -> None:
    """Create logs folder and files when missing."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("timestamp|event|path|classification|message\n", encoding="utf-8")
    if not STATS_FILE.exists():
        STATS_FILE.write_text(
            json.dumps({"total_files_scanned": 0, "suspicious_activity_count": 0}, indent=2),
            encoding="utf-8",
        )


def is_inside_test_folder(path: Path) -> bool:
    """Safety check: only process events inside test_folder."""
    try:
        path.resolve().relative_to(TEST_FOLDER)
        return True
    except ValueError:
        return False


class RansomwareMonitor(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.event_times: deque[float] = deque()
        self.stats = self.load_stats()

    def load_stats(self) -> dict:
        try:
            return json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"total_files_scanned": 0, "suspicious_activity_count": 0}

    def save_stats(self) -> None:
        STATS_FILE.write_text(json.dumps(self.stats, indent=2), encoding="utf-8")

    def append_log(self, event_name: str, path_text: str, classification: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp}|{event_name}|{path_text}|{classification}|{message}\n")

    def register_change_and_get_count(self) -> int:
        now = time.time()
        self.event_times.append(now)
        while self.event_times and now - self.event_times[0] > WINDOW_SECONDS:
            self.event_times.popleft()
        return len(self.event_times)

    def process_event(self, event_name: str, path: Path, note: str) -> None:
        if not is_inside_test_folder(path):
            return

        change_count = self.register_change_and_get_count()
        classification = "Ransomware" if change_count >= RAPID_CHANGE_THRESHOLD else "Normal"

        if change_count >= RAPID_CHANGE_THRESHOLD:
            print("⚠ Ransomware detected!")

        self.stats["total_files_scanned"] = self.stats.get("total_files_scanned", 0) + 1
        if classification == "Ransomware":
            self.stats["suspicious_activity_count"] = self.stats.get("suspicious_activity_count", 0) + 1

        relative_path = path.relative_to(TEST_FOLDER)
        self.append_log(
            event_name=event_name,
            path_text=str(relative_path),
            classification=classification,
            message=f"changes_last_10s={change_count}; {note}",
        )
        self.save_stats()

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self.process_event("modified", Path(event.src_path), "file modification")

    def on_moved(self, event: FileMovedEvent) -> None:
        if event.is_directory:
            return

        source = Path(event.src_path)
        destination = Path(event.dest_path)
        if is_inside_test_folder(destination):
            note = f"file rename: {source.name} -> {destination.name}"
            if destination.suffix == ".locked":
                note += "; .locked extension detected"
            self.process_event("renamed", destination, note)

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        note = "file created"
        if path.suffix == ".locked":
            note += "; .locked extension detected"
        self.process_event("created", path, note)


def start_monitor() -> None:
    TEST_FOLDER.mkdir(parents=True, exist_ok=True)
    ensure_log_files()

    monitor = RansomwareMonitor()
    observer = Observer()
    observer.schedule(monitor, str(TEST_FOLDER), recursive=True)

    print(f"Monitoring folder: {TEST_FOLDER}")
    print("Press Ctrl+C to stop monitoring.")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_monitor()
