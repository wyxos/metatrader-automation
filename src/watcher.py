import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            self.process.kill()
        self.process = subprocess.Popen(['python', self.script_name], shell=False)

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Change detected in {event.src_path}. Restarting script...")
            self.restart_script()

if __name__ == "__main__":
    script_to_watch = "validate_trade_signal.py"  # Replace with your script name
    event_handler = ChangeHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
