import os
import platform
import uuid
import time
import socket

def get_domain():
    if platform.system() == "Windows":
        return os.environ.get("USERDOMAIN")
    else:
        fqdn = socket.getfqdn()
        parts = fqdn.split('.')
        return '.'.join(parts[1:]) if len(parts) > 1 else None

def get_system_info() -> dict:
    """
    Gathers various pieces of system and hardware information.
    """
    return {
        "computer": platform.node(),
        "user": os.getlogin(),
        "domain": get_domain(), # This is harder to get reliably, placeholder for now
        "os": platform.system(),
        "osVersion": platform.release(),
        # Use the MAC address to generate a stable hardware ID
        "hwid": hex(uuid.getnode()) 
    }

def get_timezone_offset() -> int:
    """
    Gets the local timezone offset from UTC in milliseconds.
    """
    # time.timezone gives the offset in seconds for non-DST.
    # We negate it because the API likely expects a positive value for zones west of UTC.
    return -time.timezone * 1000