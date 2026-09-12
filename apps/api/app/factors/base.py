from abc import ABC, abstractmethod
from typing import Any

class Factor(ABC):
    name: str
    @abstractmethod
    def calculate(self, dataset: Any) -> Any: ...
    @abstractmethod
    def validate_inputs(self, dataset: Any) -> None: ...
    @abstractmethod
    def describe(self) -> dict[str, str]: ...