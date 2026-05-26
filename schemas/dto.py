from pydantic import BaseModel, Field

class UserInfo(BaseModel):
    id    :int      = Field(examples=[0, 1, 2], description="사용자 식별자")
    name  :str      = Field(examples=["냐우기", "김민혁", "굴렁쇠"], description="사용자 이름")
    email :str|None = Field(examples=["nyaugi@nyug.com", "minhyuk.kim@diquest.com", "circle@circle.com"], description="사용자 이메일")