from . import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Float, ARRAY, JSON, ForeignKey
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, comment="사용자 ID", autoincrement=True)
    name:Mapped[str] = mapped_column(String(50), comment="사용자 이름")
    email:Mapped[str] = mapped_column(String(50), comment="사용자 이메일", nullable=True)
    
class StepHistory(Base):
    __tablename__ = "step_history"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, comment="ID", autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), comment="사용자 ID")
    start_datetime:Mapped[str] = mapped_column(String(20), comment="계단오르기 시작시간")
    end_datetime:Mapped[str] = mapped_column(String(20), comment="계단오르기 종료시간")
    duration:Mapped[int] = mapped_column(Integer, comment="소요시간")
    level:Mapped[int] = mapped_column(Integer, comment="오른 층수")
    rest_count:Mapped[int] = mapped_column(Integer, comment="휴식 횟수", nullable=True)
    rest_level:Mapped[list[int]] = mapped_column(JSON, comment="휴식 층수", nullable=True)
    heartbeat:Mapped[float] = mapped_column(Float, comment="평균 심박수", nullable=True)