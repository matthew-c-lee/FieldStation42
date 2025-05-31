import json
import os
import time
import traceback
from config.config import APP_CONFIG

def read_status():
    try:
        with open(APP_CONFIG.status_socket_path, "r") as fifo:
            line = fifo.readline()
            status = json.loads(line)
            return {
                "channel": status.get("channel_number", -1),
                "name": status.get("network_name", ""),
                "title": status.get("title", ""),
            }
    except Exception as e:
        traceback.print_exc()
        return {"channel": -1, "name": ""}

def write_command(message: dict):
    """Takes a dictionary command"""
    message = json.dumps(message) + "\n"
    print("Writing to FIFO:", message)

    if not os.path.exists(APP_CONFIG.channel_socket_path):
        raise Exception(f"FIFO not found: {APP_CONFIG.channel_socket_path}")
    with open(APP_CONFIG.channel_socket_path, "w") as fifo:
        fifo.write(message)
        fifo.flush()

    # Give the player a moment to update status
    time.sleep(.25)

    status = read_status()
    return status