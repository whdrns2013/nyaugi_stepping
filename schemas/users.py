from pydantic import BaseModel, Field
from schemas.dto import UserInfo

class CreateUserRequestBody(BaseModel):
    name:str = Field(examples=[], description="사용자 이름")
    email:str = Field(examples=[], description="사용자 이메일")

class CreateUserResponseBody(BaseModel):
    id:str|int|None = Field(examples=[0], description="등록된 사용자 id", default=None)
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class UpdateUserRequestBody(BaseModel):
    id:int = Field(examples=[1], description="사용자 ID")
    name:str|None = Field(examples=["김민혁"], description="사용자 이름 (수정할 경우)")
    email:str|None = Field(examples=["minhyuk@example.com"], description="사용자 이메일 (수정할 경우)")

class UpdateUserResponseBody(BaseModel):
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class DeleteUserRequestBody(BaseModel):
    id:int = Field(examples=[1], description="사용자 ID")

class DeleteUserResponseBody(BaseModel):
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)

class RetrieveUserInfoByNameRequestBody(BaseModel):
    name:str = Field(examples=["냐우기", "김민혁"], description="사용자 이름")

class RetrieveUserInfoByNameResponseBody(BaseModel):
    user_list:list[UserInfo] = Field(examples=[[UserInfo(id=0, name="nyaugi", email="nyaugi@nyaug.com")]], description="유저 목록")
    status_code:str          = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None         = Field(examples=[""], description="실패에 대한 메시지", default=None)

class RetrieveAllUsersResponseBody(BaseModel):
    user_list:list[UserInfo] = Field(examples=[], description="모든 유저 목록")
    status_code:str = Field(examples=["0"], description="상태 코드 (0:성공/1:실패)")
    message:str|None = Field(examples=[""], description="실패에 대한 메시지", default=None)
