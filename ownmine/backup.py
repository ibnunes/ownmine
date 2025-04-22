import shutil
import os
from datetime import datetime

def backup_local(server_config):
    source = server_config['path']
    destination = server_config['backup']['local']
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = os.path.join(destination, f"{server_config['name']}_{timestamp}")
    shutil.copytree(source, backup_path)
