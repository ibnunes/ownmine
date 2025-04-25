import tempfile
from contextlib import contextmanager

@contextmanager
def _str_context(s: str):
    yield s

def mktemp(dry_run: bool = False):
    """Returns a mock temporary folder if dry_run, or a context manager for a real temporary file otherwise."""
    if dry_run:
        return _str_context("/tmp/dryrun")
    return tempfile.TemporaryDirectory()
