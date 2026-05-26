from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from enum import Enum

# ========== Enum ========== #
class RDBDataSourceType(str, Enum):
    MARIADB = "MARIADB"

# ========== Interface ========== #

class DataSourceHandler(ABC):
    def __init__(self, data_source_type, config:Dict[str,Any]):
        self.data_source_type = data_source_type
        self.config = config
    @abstractmethod
    def create(self) -> None:
        pass
    @abstractmethod
    def retrieve(self) -> Any:
        pass
    @abstractmethod
    def update(self) -> None:
        pass
    @abstractmethod
    def delete(self) -> None:
        pass

class DataHandler(ABC):
    def __init__(self, data_source_handler:DataSourceHandler, config:Dict[str,Any]):
        self.data_source_handler = data_source_handler
    @abstractmethod
    def create(self, data:Optional[Any]) -> None:
        pass
    @abstractmethod
    def retrieve(self) -> Any:
        pass
    @abstractmethod
    def update(self, data:Any) -> None:
        pass
    @abstractmethod
    def delete(self) -> None:
        pass
            
# ========== Factory ========== #

# class DataSourceHandlerFactory:
#     @classmethod
#     def get_data_source_handler(cls, data_source_type:DataSourceType, config:Dict[str,Any]):
#         if data_source_type == DataSourceType.FILE : return FileDataSourceHandler(data_source_type=data_source_type, config=config)

# class DataHandlerFactory:
#     @classmethod
#     def get_data_handler(cls, data_source_handler:DataSourceHandler, config:Dict[str,Any]):
#         if data_source_handler.data_source_type == DataSourceType.FILE : return FileDataHandler(data_source_handler=data_source_handler, config=config)