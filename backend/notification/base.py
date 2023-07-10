from abc import ABC, abstractmethod

class BaseNotification(ABC):
    def __init__(self) -> None:
        super().__init__()
        pass
    
    @abstractmethod
    def send(self, message: str):
        pass