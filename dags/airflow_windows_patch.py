"""
Windows compatibility patch for Airflow.

This module applies patches to make Airflow compatible with Windows environments,
particularly addressing asyncio event loop and signal handling issues that can
occur on Windows when using Docker Desktop or WSL2.
"""

import sys
import platform


def apply_windows_patch():
    """Apply Windows-specific patches for Airflow compatibility."""
    if platform.system() == "Windows":
        # On Windows, set the asyncio event loop policy to avoid issues with
        # signal handlers and event loops in forked processes (not applicable
        # on Windows but prevents errors in certain scenarios).
        try:
            import asyncio
            if sys.version_info >= (3, 8):
                # Use ProactorEventLoop on Windows for better compatibility
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            # Best-effort: if asyncio patching fails, continue without error
            pass


# Apply patch on module import
apply_windows_patch()
