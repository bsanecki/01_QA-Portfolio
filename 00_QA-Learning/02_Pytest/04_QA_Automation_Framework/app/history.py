from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HistoryEntry:
    operation: str
    inputs: dict
    result: object
    timestamp: datetime


class CalculationHistory:
    def __init__(self, max_size=100, clock=datetime.now):
        if isinstance(max_size, bool) or not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer.")

        self.max_size = max_size
        self._clock = clock
        self._entries = []

    def add(self, operation, inputs, result):
        if not operation or not operation.strip():
            raise ValueError("Operation name cannot be empty.")

        entry = HistoryEntry(operation, dict(inputs), result, self._clock())
        self._entries.append(entry)

        if len(self._entries) > self.max_size:
            self._entries.pop(0)

        return entry

    def all(self):
        return list(self._entries)

    def last(self):
        if not self._entries:
            raise LookupError("History is empty.")

        return self._entries[-1]

    def find(self, operation):
        return [entry for entry in self._entries if entry.operation == operation]

    def clear(self):
        self._entries.clear()

    def __len__(self):
        return len(self._entries)
