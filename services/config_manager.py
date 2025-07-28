import configparser
from typing import Optional

class ConfigManager:
    """
    Manages reading from and writing to the config.ini file.
    """
    def __init__(self, filename="config.ini"):
        self.filename = filename
        self.config = configparser.ConfigParser()
        # Read the existing config file if it exists
        self.config.read(self.filename)

    def get_token(self) -> Optional[str]:
        """Reads the auth token from the config file."""
        if 'Auth' in self.config and 'token' in self.config['Auth']:
            return self.config['Auth']['token']
        return None

    def save_token(self, token: str):
        """Saves the auth token to the config file."""
        if 'Auth' not in self.config:
            self.config['Auth'] = {}
        self.config['Auth']['token'] = token
        self._write_config()

    def clear_token(self):
        """Removes the auth token from the config file."""
        if 'Auth' in self.config:
            self.config.remove_section('Auth')
            self._write_config()

    def _write_config(self):
        """Writes the current configuration state to the file."""
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
