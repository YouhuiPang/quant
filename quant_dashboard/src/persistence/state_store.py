from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class StateStore(ABC):
    """Abstract persistence interface for execution state."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize persistence tables."""

    @abstractmethod
    def append_table(self, table_name: str, frame: pd.DataFrame) -> None:
        """Append rows to a named table."""

    @abstractmethod
    def replace_table(self, table_name: str, frame: pd.DataFrame) -> None:
        """Replace a named table with the provided frame."""

    @abstractmethod
    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load a named table."""
