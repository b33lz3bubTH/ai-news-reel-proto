from typing import Callable, Dict, List, Any
from abc import ABC, abstractmethod

class EventManager:
    _events: Dict[str, List[Callable[[Any], None]]] = {}

    @classmethod
    def subscribe(cls, event: str, handler: Callable[[Any], None]):
        """Subscribe a function to an event."""
        if event not in cls._events:
            cls._events[event] = []
        cls._events[event].append(handler)

    @classmethod
    def emit(cls, event: str, data: Any):
        """Trigger all handlers for an event."""
        for handler in cls._events.get(event, []):
            handler(data)


class EventHandler(ABC):
    @abstractmethod
    def handle(self, data: dict):
        """Handle event data."""
        pass
