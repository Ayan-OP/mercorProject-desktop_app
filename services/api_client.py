import httpx
from typing import Optional, Dict, Any, List
from .config_manager import ConfigManager

class APIClient:
    """
    A client to handle all communication with the T3 backend API.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api"):
        self.base_url = base_url
        self.client = httpx.Client()
        self.config = ConfigManager()
        self._token: Optional[str] = self.config.get_token()
        
        if self._token:
            self.client.headers["Authorization"] = f"Bearer {self._token}"

    @property
    def token(self) -> Optional[str]:
        return self._token

    @token.setter
    def token(self, value: Optional[str]):
        self._token = value
        if self._token:
            self.client.headers["Authorization"] = f"Bearer {self._token}"
            self.config.save_token(self._token)
        else:
            self.client.headers.pop("Authorization", None)
            self.config.clear_token()

    def login(self, email: str, password: str) -> bool:
        """Logs in the user and stores the access token."""
        try:
            response = self.client.post(
                f"{self.base_url}/auth/login",
                data={"username": email, "password": password}
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            return bool(self.token)
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def logout(self):
        """Logs out the user by clearing the token."""
        self.token = None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Fetches the details of the currently logged-in user."""
        if not self.token: return None
        try:
            response = self.client.get(f"{self.base_url}/auth/me")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get user: {e}")
            return None

    def get_projects(self) -> Optional[List[Dict[str, Any]]]:
        """Fetches the full details for all projects assigned to the current user."""
        if not self.token: return None
        user = self.get_current_user()
        if not user or 'projects' not in user: return []
        project_ids = user['projects']
        if not project_ids: return []
        
        projects_data = []
        try:
            for project_id in project_ids:
                res = self.client.get(f"{self.base_url}/v1/project/{project_id}")
                res.raise_for_status()
                projects_data.append(res.json())
            return projects_data
        except Exception as e:
            print(f"Failed to get project details: {e}")
            return None

    def get_tasks_for_project(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetches tasks for a specific project that are assigned to the current user."""
        if not self.token or not project_id:
            return None
        try:
            # The backend route will automatically filter by the logged-in user from the token
            response = self.client.get(f"{self.base_url}/v1/task", params={"projectId": project_id})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get tasks for project {project_id}: {e}")
            return None
        
    def get_tasks_by_task_id(self, task_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetches task that are assigned to the current user."""
        if not self.token or not task_id:
            return None
        try:
            # The backend route will automatically filter by the logged-in user from the token
            response = self.client.get(f"{self.base_url}/v1/task/{task_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get task for {task_id}: {e}")
            return None
        
    def send_time_window(self, window_data: dict) -> bool:
        """Sends a collected time window to the backend."""
        if not self.token:
            return False
        try:
            res = self.client.post(f"{self.base_url}/v1/time-entries", json=window_data)
            res.raise_for_status()
            print("Successfully sent time window to backend.")
            return True
        except httpx.HTTPStatusError as e:
            print(f"Failed to send time window: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while sending time window: {e}")
            return False
        
    def get_task_time(self, employee_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Fetches the total time a user has spent on a specific task."""
        if not self.token or not employee_id or not task_id:
            return None
        try:
            params = {"employeeId": employee_id, "taskId": task_id}
            response = self.client.get(f"{self.base_url}/v1/analytics/task-time", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get task time for task {task_id}: {e}")
            return None
