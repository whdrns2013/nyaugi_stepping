from utils.data_handler import DataSourceHandler, DataHandler
from typing import List, Dict, Any, Optional
import os

class FileDataSourceHandler(DataSourceHandler):
    def __init__(self, data_source_type, config:Dict[str,Any]):
        super().__init__(data_source_type, config)
        self.dir_path = config.get("dir_path")
    def create(self) -> None:
        os.makedirs(self.dir_path, exist_ok=True)
    def retrieve(self) -> List[str]:
        return os.listdir(self.dir_path)
    def update(self) -> None:
        pass
    def delete(self) -> None:
        return os.rmdir(path=self.dir_path)

class FileDataHandler(DataHandler):
    def __init__(self, data_source_handler:FileDataSourceHandler, config:Dict[str,Any]):
        super().__init__(data_source_handler, config)
        self.dir_path = self.data_source_handler.dir_path
        self.file_name = config.get("file_name", "noname")
        self.file_path:str = os.path.join(self.dir_path, self.file_name)
        self.encoding = config.get("encoding", "utf-8")
    def create(self, data:Optional[Any]) -> None:
        with open(self.file_path, 'w', encoding=self.encoding) as f:
            if data is not None:
                f.write(data)
    def retrieve(self) -> Any:
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                data = f.readlines()
            return '\n'.join(data)
        except FileNotFoundError:
            return ''
    def update(self, data:str) -> None:
        with open(self.file_path, 'a', encoding=self.encoding) as f:
            f.write(data)
    def delete(self) -> None:
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다. : {self.file_path}")