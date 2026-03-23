import re
from urllib.parse import urlparse


_WINDOWS_DRIVE_PATH = re.compile(r"^[a-zA-Z]:[\\/]")
_UNC_PATH = re.compile(r"^[\\/]{2}[^\\/]+[\\/][^\\/]+")


def is_local_path(path_str: str) -> bool:
    """Return True if path_str is a local filesystem path and not a remote URL or scheme.

    Disallows http(s), s3, ftp, and other URI schemes. Allows file:// and plain filesystem paths.
    """
    if not path_str:
        return False
    if _WINDOWS_DRIVE_PATH.match(path_str) or _UNC_PATH.match(path_str):
        return True
    parsed = urlparse(path_str)
    # If a scheme exists and it is not file, treat as remote
    if parsed.scheme and parsed.scheme != 'file':
        return False
    lower = path_str.lower()
    if lower.startswith('http://') or lower.startswith('https://') or lower.startswith('s3://') or lower.startswith('ftp://'):
        return False
    # Catch other obvious URI patterns
    if '://' in path_str and parsed.scheme == '':
        return False
    return True


def ensure_local_path_or_raise(path_str: str, message: str = None):
    if not is_local_path(path_str):
        msg = message or f"Path is not local or uses a remote scheme: {path_str}"
        raise RuntimeError(msg)
