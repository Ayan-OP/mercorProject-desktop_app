# Mercor Time Tracker - Desktop Application

This is the desktop client for the mercor Time Tracker system. It's a native application built with Python and PySide6 that allows employees to securely log in, view their assigned work, and track their time.

---

## 🏛️ Architecture & System Design

The application is designed to be responsive and efficient by separating its core responsibilities into distinct modules.

* **Technology Stack**:
    * **UI Framework**: PySide6 (Qt for Python) was chosen to create a lightweight, fast, and truly native user interface, providing a better user experience and lower resource usage compared to web-based wrappers like Electron.
    * **HTTP Client**: `httpx` is used for all communication with the backend API, providing a modern, asynchronous-ready interface.
    * **System Information**: `psutil` and `platform` are used to gather necessary hardware and OS details to send with time tracking data, providing proof of work.

* **Core Architecture**:
    * **Services (`services/`)**: This layer contains modules like the `api_client.py` and `config_manager.py`. It abstracts all external interactions, such as making API calls and saving/loading the local configuration.
    * **UI (`ui/`)**: This layer contains all the visual components, such as the `LoginWindow` and `MainWindow`. These files are only responsible for displaying data and capturing user input.
    * **Workers (`workers/`)**: This layer contains the `TrackingWorker` (`QThread`), which runs all the time-tracking logic on a separate background thread. **This is a critical design choice to prevent the UI from freezing** while the timer is running, ensuring the application remains smooth and responsive at all times. The worker communicates with the UI safely using Qt's signals and slots mechanism.

## ✨ Features

* **Secure Login**: Authenticates with the backend API using email and password.
* **Persistent Sessions**: Securely saves the authentication token locally, allowing for automatic login on subsequent launches.
* **Project & Task Viewing**: Fetches and displays a list of projects and tasks assigned to the logged-in user.
* **Task Segregation**: Intelligently separates tasks into "My Tasks" and "Other Tasks" for clarity.
* **Permission-Based Tracking**: Only allows time to be tracked against tasks explicitly assigned to the user.
* **Live Time Tracking**: A background worker tracks time in real-time and updates the UI every second.
* **Data Sync**: Periodically sends "time windows" containing system and hardware information to the backend API.
* **Total Time Display**: Shows the total time a user has already logged for their assigned tasks.

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* The mercor Backend API must be running.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>/desktop_app/
```

### 2. Setup Environment
- Create a virtual environment and install the required dependencies.
```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
- With the backend server running, you can start the desktop application.
```
python main.py
```

## 📦 Packaging for Distribution
- To create a single, standalone executable file (```.exe``` on Windows) that can be shared with users, we use PyInstaller.

### 1. Install PyInstaller
```
pip install pyinstaller
```

### 2. Run the Build Command
- From the ```desktop_app``` directory, run the following command in your terminal:
```
pyinstaller --onefile --windowed --name "mercor-Tracker" main.py
```
- ```--onefile```: Bundles everything into a single executable.

- ```--windowed```: Prevents the command prompt from showing behind the app.

- ```--name```: Sets the name of the final application file.

### 3. Find the Executable
- After the command finishes, your downloadable application will be located in the ```dist/``` folder. You can share this ```mercor-Tracker.exe``` file with your employees.
