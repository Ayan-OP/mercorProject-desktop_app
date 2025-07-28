import sys
from PySide6.QtWidgets import QApplication
from services.api_client import APIClient
from ui.login_window import LoginWindow
from ui.main_window import MainWindow 

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.api_client = APIClient()
        self.main_window = None
        self.login_window = None
        
        # Check if we are already logged in from a previous session
        user_data = self.api_client.get_current_user()
        if user_data:
            print("Already logged in. Showing main window.")
            self.show_main_window(user_data)
        else:
            print("Not logged in. Showing login window.")
            self.show_login_window()

    def show_login_window(self):
        """Creates and shows the login window."""
        self.login_window = LoginWindow(self.api_client)
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self, user_data: dict):
        """Creates and shows the main tracker window after a successful login."""
        print(f"Welcome, {user_data.get('name', 'User')}!")
        self.main_window = MainWindow(self.api_client, user_data)
        # --- CONNECT LOGOUT SIGNAL ---
        self.main_window.logout_requested.connect(self.handle_logout)
        self.main_window.show()

    def handle_logout(self):
        """Closes the main window and shows the login window."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.show_login_window()

    def run(self):
        """Starts the application's event loop."""
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = MainApplication()
    main_app.run()
