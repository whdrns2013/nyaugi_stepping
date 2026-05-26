from utils.data_handler import DataSourceHandler, DataHandler
from typing import List, Dict, Any, Optional
from utils.data_handler import RDBDataSourceType
from pydantic import BaseModel
import pymysql
from pymysql.cursors import Cursor

class RDBConfig(BaseModel):
    host:str
    port:int
    user:str
    password:str
    database:str

class RDBDataSourceHandler(DataSourceHandler):
    def __init__(self, data_source_type:RDBDataSourceType, config:Dict[str,Any]):
        super().__init__(data_source_type, config)
    def create(self) -> None:
        pass
    def retrieve(self) -> List[str]:
        pass
    def update(self) -> None:
        pass
    def delete(self) -> None:
        pass
    def connect(self) -> None:
        pass
    def close(self) -> None:
        pass

class RDBDataHandler(DataHandler):
    def __init__(self, data_source_type:RDBDataSourceType, config:Dict[str,Any]):
        super().__init__(data_source_type, config)
    def create(self, data:Optional[Any]) -> None:
        pass
    def retrieve(self) -> Any:
        pass
    def update(self, data:str) -> None:
        pass
    def delete(self) -> None:
        pass
    

# MariaDB
class MariaDBDataSourceHandler(RDBDataSourceHandler):
    def __init__(self, data_source_type:RDBDataSourceType, config:Dict[str,Any]):
        super().__init__(data_source_type, config)
        self.config = RDBConfig(**config)
    def create(self) -> None:
        pass # TODO: 추후 개발 : 스키마(테이블) 생성
    def retrieve(self) -> List[str]:
        pass # TODO: 추후 개발 : 스키마(테이블) 조회
    def update(self) -> None:
        pass # TODO: 추후 개발 : 스키마(테이블) 수정
    def delete(self) -> None:
        pass # TODO: 추후 개발 : 스키마(테이블) 삭제
    def connect(self):
        if not hasattr(self, "conn") or self.conn.open is False:
            self.conn = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                cursorclass=pymysql.cursors.DictCursor
            )
        return self.conn
    def get_cursor(self) -> Cursor:
        return self.connect().cursor()
    def close(self) -> None:
        if hasattr(self, "conn") and self.conn.open:
            self.conn.close()

class MariaDBDataHandler(RDBDataHandler):
    def __init__(self, data_source_type:RDBDataSourceType, config:Dict[str,Any]|None):
        super().__init__(data_source_type, config)
        self.data_source_handler = RDBDataSourceHandlerFactory.create(data_source_type, config)
    def create(self, data:Optional[Any]) -> None:
        pass # TODO: 추후 개발 : 데이터 삽입
    def retrieve(self, query:str, params:tuple=()) -> Any:
        try:
            with self.data_source_handler.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            self.data_source_handler.close()
    def update(self, data:str) -> None:
        pass # TODO: 추후 개발 : 데이터 수정
    def delete(self) -> None:
        pass # TODO: 추후 개발 : 데이터 삭제

# Factory
class RDBDataSourceHandlerFactory:
    REGISTRY = {
        RDBDataSourceType.MARIADB : MariaDBDataSourceHandler
        }
    @classmethod
    def create(cls, data_source_type:RDBDataSourceType, config:Dict[str,Any]):
        return cls.REGISTRY[data_source_type](data_source_type, config)
    
class RDBDataHandlerFactory:
    REGISTRY = {
        RDBDataSourceType.MARIADB : MariaDBDataHandler
        }
    @classmethod
    def create(cls, data_source_type:RDBDataSourceType, config:Dict[str,Any]|None):
        return cls.REGISTRY[data_source_type](data_source_type, config)