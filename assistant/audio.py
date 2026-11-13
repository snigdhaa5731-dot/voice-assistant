"""
Audio utility module for suppressing ALSA/JACK driver warnings on Linux.
"""

import os
import sys
from contextlib import contextmanager

@contextmanager
def suppress_c_stderr():
    """
    Context manager to suppress low-level C stderr outputs (like ALSA / JACK errors)
    that clutter the terminal during audio device queries.
    """
    try:
        # Duplicate stderr file descriptor
        stderr_fd = sys.stderr.fileno()
        saved_stderr = os.dup(stderr_fd)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, stderr_fd)
        os.close(devnull)
        try:
            yield
        finally:
            # Restore original stderr
            os.dup2(saved_stderr, stderr_fd)
            os.close(saved_stderr)
    except Exception:
        # Fallback if fileno() is unavailable (e.g. redirected or mocked environment)
        yield
