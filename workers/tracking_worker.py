import time
from PySide6.QtCore import QThread, Signal
from services.system_info import get_system_info, get_timezone_offset

class TrackingWorker(QThread):
    """
    A background thread that handles the time tracking logic.
    """
    # Signals to communicate with the main UI thread
    time_updated = Signal(int) # Emits the elapsed seconds
    window_ready_to_send = Signal(dict) # Emits the complete time window data

    def __init__(self, project_id: str, task_id: str):
        super().__init__()
        self.project_id = project_id
        self.task_id = task_id
        self._is_running = False
        self.elapsed_seconds = 0
        self.chunk_start_time = 0

    def run(self):
        """The main loop for the background thread."""
        self._is_running = True
        self.chunk_start_time = int(time.time() * 1000) # Start time in milliseconds
        
        while self._is_running:
            time.sleep(1)
            if not self._is_running:
                break
                
            self.elapsed_seconds += 1
            self.time_updated.emit(self.elapsed_seconds)

            # Every 1 minute (60 seconds), package and send the time window
            if self.elapsed_seconds % 60 == 0:
                self.package_and_send_window()
                # Start a new chunk
                self.chunk_start_time = int(time.time() * 1000)

    def stop(self):
        """Stops the tracking thread."""
        self._is_running = False
        # Send any remaining time before stopping
        if self.elapsed_seconds % 60 != 0:
            self.package_and_send_window()
        print("Tracking worker stopped.")

    def package_and_send_window(self):
        """Gathers all data and emits the signal to send it."""
        end_time = int(time.time() * 1000)
        
        window_data = {
            "start": self.chunk_start_time,
            "end": end_time,
            "timezoneOffset": get_timezone_offset(),
            "projectId": self.project_id,
            "taskId": self.task_id,
            **get_system_info() # Merge in all the system info
        }
        
        self.window_ready_to_send.emit(window_data)
        print(f"Packaged a time window of {end_time - self.chunk_start_time}ms")

