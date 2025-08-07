from abc import ABC, abstractmethod

class BaseLoader(ABC):
    @abstractmethod
    def load(self, uri: str) -> list[dict]:
        """Verilen URI'den dokümanları yükler."""
        pass