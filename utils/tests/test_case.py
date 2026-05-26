from abc import ABC, abstractmethod

class TestCase(ABC):
    @abstractmethod
    def run(self) -> str:
        raise NotImplementedError
    
