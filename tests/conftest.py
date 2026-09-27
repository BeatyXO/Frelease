"""Compatibility shim for genlayer-test on Windows direct-mode runners."""
import os
import tempfile
if os.name == "nt":
    _unlink = os.unlink
    def _unlink_windows_safe(path, *args, **kwargs):
        try: return _unlink(path, *args, **kwargs)
        except PermissionError:
            root=os.path.abspath(tempfile.gettempdir()).lower();candidate=os.path.abspath(os.fspath(path)).lower()
            if candidate.startswith(root + os.sep): return None
            raise
    os.unlink = _unlink_windows_safe
