from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Qt, Signal
from services.api_client import APIClient
from workers.tracking_worker import TrackingWorker

class MainWindow(QWidget):
    logout_requested = Signal()

    def __init__(self, api_client: APIClient, user_data: dict):
        super().__init__()
        self.api_client = api_client
        self.user_data = user_data
        self.my_task_ids = set()
        self.setWindowTitle("T3 Tracker")
        
        self.is_tracking = False
        self.tracking_worker = None
        
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        self.welcome_label = QLabel(f"Welcome, {self.user_data.get('name', 'User')}!")
        
        self.project_label = QLabel("Select a Project:")
        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Loading projects...")
        self.project_combo.currentIndexChanged.connect(self.on_project_selected)

        # --- Task Layout with Time Display ---
        task_layout = QHBoxLayout()
        self.task_label = QLabel("Select a Task:")
        self.task_time_label = QLabel("") # New label for displaying time
        self.task_time_label.setAlignment(Qt.AlignRight)
        task_layout.addWidget(self.task_label)
        task_layout.addWidget(self.task_time_label)

        self.task_combo = QComboBox()
        self.task_combo.setPlaceholderText("Select a project first")
        self.task_combo.setEnabled(False)
        self.task_combo.currentIndexChanged.connect(self.on_task_selected)

        self.timer_label = QLabel("00:00:00")
        font = self.timer_label.font(); font.setPointSize(24); self.timer_label.setFont(font)
        
        self.start_stop_button = QPushButton("Start Tracking")
        self.start_stop_button.setEnabled(False)
        self.start_stop_button.clicked.connect(self.toggle_tracking)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        
        main_layout.addWidget(self.welcome_label)
        main_layout.addWidget(self.project_label)
        main_layout.addWidget(self.project_combo)
        main_layout.addLayout(task_layout) # Add the horizontal layout
        main_layout.addWidget(self.task_combo)
        main_layout.addWidget(self.timer_label)
        main_layout.addWidget(self.start_stop_button)
        main_layout.addWidget(self.logout_button)
        
        self.setLayout(main_layout)
        self.setFixedSize(300, 340)

    def load_projects(self):
        projects = self.api_client.get_projects()
        self.project_combo.clear()
        self.project_combo.addItem("Select a project...", userData=None)
        if projects:
            for project in projects:
                self.project_combo.addItem(project['name'], userData=project['id'])
        else:
            self.project_combo.setPlaceholderText("No projects found")

    def on_project_selected(self, index: int):
        project_id = self.project_combo.itemData(index)
        self.task_combo.clear()
        self.task_time_label.setText("")
        if project_id:
            self.task_combo.setEnabled(True)
            self.task_combo.setPlaceholderText("Loading tasks...")
            self.load_tasks(project_id)
        else:
            self.task_combo.setEnabled(False)
            self.task_combo.setPlaceholderText("Select a project first")
        self.update_start_button_state()

    def on_task_selected(self, index: int):
        """Called when the task selection changes to update time display and button state."""
        self.update_start_button_state()
        self.update_task_time_display()

    def load_tasks(self, project_id: str):
        """
        Fetches all tasks for the project and populates the dropdown.
        Fetches full details for "My Tasks" and uses summary for "Other Tasks".
        """
        all_tasks_summary = self.api_client.get_tasks_for_project(project_id)
        self.task_combo.clear()
        self.my_task_ids.clear()

        if all_tasks_summary:
            my_tasks_summary = []
            other_tasks_summary = []
            my_user_id = self.user_data.get('id')

            for task_summary in all_tasks_summary:
                if my_user_id in task_summary.get('employees', []):
                    my_tasks_summary.append(task_summary)
                    self.my_task_ids.add(task_summary['id'])
                else:
                    other_tasks_summary.append(task_summary)
            
            # --- CORRECTED LOGIC: Fetch full details for "My Tasks" ---
            if my_tasks_summary:
                self.task_combo.addItem("--- My Tasks ---")
                self.task_combo.model().item(self.task_combo.count() - 1).setEnabled(False)
                for task_summary in my_tasks_summary:
                    # Fetch full details for this specific task
                    task_details = self.api_client.get_tasks_by_task_id(task_summary['id'])
                    if task_details:
                        # Use the detailed name from the full response
                        self.task_combo.addItem(task_details['name'], userData=task_details['id'])
                    else:
                        # Fallback to the summary name if the API call fails
                        self.task_combo.addItem(task_summary['name'], userData=task_summary['id'])

            if my_tasks_summary and other_tasks_summary:
                self.task_combo.insertSeparator(self.task_combo.count())

            # Use summary data directly for "Other Tasks"
            if other_tasks_summary:
                self.task_combo.addItem("--- Other Tasks ---")
                self.task_combo.model().item(self.task_combo.count() - 1).setEnabled(False)
                for task_summary in other_tasks_summary:
                    self.task_combo.addItem(task_summary['name'], userData=task_summary['id'])
        else:
            self.task_combo.setPlaceholderText("No tasks found")
        
        self.update_start_button_state()
        self.update_task_time_display()

    def update_task_time_display(self):
        """Fetches and displays the total time for the selected task if it's assigned to the user."""
        task_id = self.task_combo.currentData()
        if task_id and task_id in self.my_task_ids:
            employee_id = self.user_data.get('id')
            time_data = self.api_client.get_task_time(employee_id, task_id)
            if time_data:
                ms = time_data.get('totalTimeMillis', 0)
                self.task_time_label.setText(f"Total: {ms} ms")
            else:
                self.task_time_label.setText("Total: 0 ms")
        else:
            self.task_time_label.setText("")

    def update_start_button_state(self):
        selected_task_id = self.task_combo.currentData()
        if selected_task_id and selected_task_id in self.my_task_ids:
            self.start_stop_button.setEnabled(True)
        else:
            self.start_stop_button.setEnabled(False)

    def toggle_tracking(self):
        if self.is_tracking:
            if self.tracking_worker: self.tracking_worker.stop()
            self.is_tracking = False
            self.start_stop_button.setText("Start Tracking")
            self.project_combo.setEnabled(True)
            self.task_combo.setEnabled(True)
            self.update_timer_display(0)
        else:
            project_id = self.project_combo.currentData()
            task_id = self.task_combo.currentData()
            self.is_tracking = True
            self.start_stop_button.setText("Stop Tracking")
            self.project_combo.setEnabled(False)
            self.task_combo.setEnabled(False)
            self.tracking_worker = TrackingWorker(project_id, task_id)
            self.tracking_worker.time_updated.connect(self.update_timer_display)
            self.tracking_worker.window_ready_to_send.connect(self.api_client.send_time_window)
            self.tracking_worker.start()

    def update_timer_display(self, seconds: int):
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        self.timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def handle_logout(self):
        if self.is_tracking: self.tracking_worker.stop()
        self.api_client.logout()
        self.logout_requested.emit()
        self.close()

    def closeEvent(self, event):
        if self.is_tracking and self.tracking_worker: self.tracking_worker.stop()
        event.accept()
