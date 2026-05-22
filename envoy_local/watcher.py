"""File watcher that auto-regenerates Envoy config on source changes."""

import time
import os
import logging
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ConfigWatcher:
    """Watches a config file for changes and triggers a callback on modification."""

    def __init__(
        self,
        source_path: str,
        on_change: Callable[[str], None],
        poll_interval: float = 1.0,
    ):
        self.source_path = Path(source_path)
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._last_mtime: Optional[float] = None
        self._running = False

    def _get_mtime(self) -> Optional[float]:
        try:
            return os.path.getmtime(self.source_path)
        except FileNotFoundError:
            return None

    def _check_and_trigger(self) -> bool:
        """Check if file changed; trigger callback if so. Returns True if changed."""
        mtime = self._get_mtime()
        if mtime is None:
            logger.warning("Watched file not found: %s", self.source_path)
            return False
        if self._last_mtime is None or mtime != self._last_mtime:
            self._last_mtime = mtime
            if self._last_mtime is not None:
                logger.info("Change detected in %s, regenerating config...", self.source_path)
                self.on_change(str(self.source_path))
            return True
        return False

    def start(self) -> None:
        """Start the watch loop (blocking)."""
        logger.info(
            "Watching %s for changes (poll interval: %ss)",
            self.source_path,
            self.poll_interval,
        )
        self._running = True
        # Initialise mtime without triggering callback
        self._last_mtime = self._get_mtime()
        try:
            while self._running:
                self._check_and_trigger()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logger.info("Watcher stopped.")
        finally:
            self._running = False

    def stop(self) -> None:
        """Signal the watch loop to stop."""
        self._running = False
