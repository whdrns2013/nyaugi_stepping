from pydantic import BaseModel, Field

class CreateStepHistoryRequestBody(BaseModel):
    user_id:list[int] = Field(examples=[[5, 6, 7, 8],0], description="사용자 ID/리스트로 여러 사용자를 담을 수도 있음")
    start_datetime:str = Field(examples=["2026-04-22  12:05:00"], description="시작 일시")
    end_datetime:str = Field(examples=["2026-04-22  12:12:00"], description="종료 일시")
    level:int|None = Field(examples=[19], description="계단으로 오른 층수")
    rest_count:int|None = Field(examples=[1], description="휴식한 횟수", default=None)
    rest_level:list[int]|None = Field(examples=[[12, 15]], description="휴식한 층수", default=None)
    heartbeat:float|None = Field(examples=[167], description="평균 심박수", default=None)

class CreateStepHistoryResponse(BaseModel):
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class UpdateStepHistoryRequestBody(BaseModel):
    id:int = Field(examples=[1], description="이력 ID")
    start_datetime:str|None = Field(examples=["2026-04-22 12:05:00"], description="수정할 시작 일시", default=None)
    end_datetime:str|None = Field(examples=["2026-04-22 12:12:00"], description="수정할 종료 일시", default=None)
    level:int|None = Field(examples=[20], description="수정할 층수")
    heartbeat:float|None = Field(examples=[168.0], description="수정할 심박수")
    rest_count:int|None = Field(examples=[2], description="수정할 휴식 횟수")
    rest_level:list[int]|None = Field(examples=[[10, 20]], description="수정할 휴식 층수")

class UpdateStepHistoryResponse(BaseModel):
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class DeleteStepHistoryRequestBody(BaseModel):
    id:int = Field(examples=[1], description="이력 ID")

class DeleteStepHistoryResponse(BaseModel):
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class StepHistoryInfo(BaseModel):
    id:int
    user_id:int
    name:str|None
    start_datetime:str
    end_datetime:str
    duration:int
    level:int
    rest_count:int|None
    rest_level:list[int]|None
    heartbeat:float|None

class RetrieveStepHistoryResponseBody(BaseModel):
    history_list:list[StepHistoryInfo] = Field(examples=[], description="이력 목록")
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class RetrieveStepHistoryWithNameResponseBody(BaseModel):
    history_list:list[StepHistoryInfo] = Field(examples=[], description="이력 목록")
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class CsvImportResponse(BaseModel):
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)
    success_count:int = Field(examples=[10], description="성공적으로 등록된行数", default=0)
    fail_count:int = Field(examples=[0], description="등록에 실패한行数", default=0)
    errors:list[str] = Field(examples=[], description="실패 행에 대한 에러 메시지 목록", default_factory=list)