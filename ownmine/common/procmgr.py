import psutil

def is_process_running(pid: int) -> bool:
    try:
        proc = psutil.Process(pid)
        return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False

def get_process_status(pid: int):
    try:
        return psutil.Process(pid).status()
    except:
        return None
