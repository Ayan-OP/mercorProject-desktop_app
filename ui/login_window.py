from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Signal
from services.api_client import APIClient

class LoginWindow(QWidget):
    # A signal that will be emitted when login is successful
    login_successful = Signal(dict) 

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.setWindowTitle("T3 Tracker - Login")
        self.setup_ui()

    def setup_ui(self):
        """Sets up the user interface of the login window."""
        layout = QVBoxLayout()
        
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        
        self.status_label = QLabel("") # To show status messages
        
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def attempt_login(self):
        """Handles the login button click event."""
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            self.status_label.setText("Email and password are required.")
            return

        self.login_button.setEnabled(False)
        self.status_label.setText("Logging in...")

        # Perform the login using our API client
        if self.api_client.login(email, password):
            user_data = self.api_client.get_current_user()
            if user_data:
                # If successful, emit the signal with the user data
                self.login_successful.emit(user_data)
                self.close() # Close the login window
            else:
                self.status_label.setText("Login successful, but failed to fetch user data.")
                self.login_button.setEnabled(True)
        else:
            self.status_label.setText("Login failed. Please check your credentials.")
            self.login_button.setEnabled(True)
