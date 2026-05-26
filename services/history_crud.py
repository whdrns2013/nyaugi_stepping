from models.step_data import StepHistory, User
from engine.db_engine import get_db_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from schemas.step_history import CreateStepHistoryRequestBody, CreateStepHistoryResponse, UpdateStepHistoryRequestBody, UpdateStepHistoryResponse, DeleteStepHistoryRequestBody, DeleteStepHistoryResponse, RetrieveStepHistoryResponseBody, StepHistoryInfo, CsvImportResponse
from config.enums import StatusCode
import copy
import csv
from datetime import datetime
from io import StringIO

GLOBAL_DB_ENGINE = get_db_engine()

def retrieve_all_history(engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    
    with Session() as s:
        stmt = select(StepHistory)
        datas = s.scalars(stmt).all()
    
    return RetrieveStepHistoryResponseBody(
        history_list=[StepHistoryInfo(
            id=h.id,
            user_id=h.user_id,
            start_datetime=h.start_datetime,
            end_datetime=h.end_datetime,
            duration=h.duration,
            level=h.level,
            rest_count=h.rest_count,
            rest_level=h.rest_level,
            heartbeat=h.heartbeat
        ) for h in datas],
        status_code=StatusCode.SUCCESS.value
    )

def retrieve_history_by_user_id(user_id: int|None, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        stmt = select(StepHistory.id, StepHistory.user_id, User.name, StepHistory.start_datetime, StepHistory.end_datetime, StepHistory.duration,
                      StepHistory.level, StepHistory.rest_count, StepHistory.rest_level, StepHistory.heartbeat).join(User, StepHistory.user_id == User.id)\
                      .where(StepHistory.user_id == user_id)
        datas = s.execute(stmt).all()
    
    return RetrieveStepHistoryResponseBody(
        history_list=[StepHistoryInfo(
            id=h.id,
            user_id=h.user_id,
            name=h.name,
            start_datetime=h.start_datetime,
            end_datetime=h.end_datetime,
            duration=h.duration,
            level=h.level,
            rest_count=h.rest_count,
            rest_level=h.rest_level,
            heartbeat=h.heartbeat
        ) for h in datas],
        status_code=StatusCode.SUCCESS.value
    )

def retrieve_history_by_user_name(user_name: str|None, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        stmt = stmt = select(StepHistory.id, StepHistory.user_id, User.name, StepHistory.start_datetime, StepHistory.end_datetime, StepHistory.duration,
                      StepHistory.level, StepHistory.rest_count, StepHistory.rest_level, StepHistory.heartbeat).join(User, StepHistory.user_id == User.id)\
                      .where(User.name == user_name)
        datas = s.execute(stmt).all()
    
    return RetrieveStepHistoryResponseBody(
        history_list=[StepHistoryInfo(
            id=h.id,
            user_id=h.user_id,
            name=h.name,
            start_datetime=h.start_datetime,
            end_datetime=h.end_datetime,
            duration=h.duration,
            level=h.level,
            rest_count=h.rest_count,
            rest_level=h.rest_level,
            heartbeat=h.heartbeat
        ) for h in datas],
        status_code=StatusCode.SUCCESS.value
    )

def retrieve_all_history_with_user_name(engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    
    with Session() as s:
        stmt = select(StepHistory.id, StepHistory.user_id, User.name, StepHistory.start_datetime, StepHistory.end_datetime, StepHistory.duration,
                      StepHistory.level, StepHistory.rest_count, StepHistory.rest_level, StepHistory.heartbeat).join(User, StepHistory.user_id == User.id)
        datas = s.execute(stmt).all()
    
    return RetrieveStepHistoryResponseBody(
        history_list=[StepHistoryInfo(
            id=h.id,
            user_id=h.user_id,
            name=h.name,
            start_datetime=h.start_datetime,
            end_datetime=h.end_datetime,
            duration=h.duration,
            level=h.level,
            rest_count=h.rest_count,
            rest_level=h.rest_level,
            heartbeat=h.heartbeat
        ) for h in datas],
        status_code=StatusCode.SUCCESS.value
    )

def create_step_history(data:CreateStepHistoryRequestBody,
                         engine=GLOBAL_DB_ENGINE):
    
    Session = sessionmaker(bind=engine)
    with Session() as s:
        for user_id in data.user_id:
            try:
                start = datetime.strptime(data.start_datetime, "%Y-%m-%d %H:%M:%S.%f")
                end = datetime.strptime(data.end_datetime, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                # fallback to simpler format if microseconds are missing
                start = datetime.strptime(data.start_datetime, "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(data.end_datetime, "%Y-%m-%d %H:%M:%S")
                
            diff = (end - start).seconds
            
            history = StepHistory(user_id=int(user_id),
                                   start_datetime=data.start_datetime,
                                   end_datetime=data.end_datetime,
                                   duration=diff,
                                   level=data.level)
            
            if data.rest_count is not None:
                history.rest_count = data.rest_count
            
            if data.rest_level is not None:
                history.rest_level = data.rest_level
                
            if data.heartbeat is not None:
                history.heartbeat = data.heartbeat
            
            try:
                s.add(history)
                s.commit()
            except Exception as e:
                print(e)
    
    return CreateStepHistoryResponse(
        status_code=StatusCode.SUCCESS.value
    )

def _parse_datetime(dt_str: str) -> datetime:
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

def update_step_history(data: UpdateStepHistoryRequestBody, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        history = s.get(StepHistory, data.id)
        if not history:
            return UpdateStepHistoryResponse(
                status_code=StatusCode.FAIL.value,
                message="해당 ID의 이력을 찾을 수 없습니다."
            )

        if data.start_datetime is not None:
            history.start_datetime = data.start_datetime
        if data.end_datetime is not None:
            history.end_datetime = data.end_datetime

        if data.start_datetime is not None or data.end_datetime is not None:
            new_start = _parse_datetime(data.start_datetime) if data.start_datetime else _parse_datetime(history.start_datetime)
            new_end = _parse_datetime(data.end_datetime) if data.end_datetime else _parse_datetime(history.end_datetime)
            history.duration = (new_end - new_start).seconds

        if data.level is not None:
            history.level = data.level
        if data.heartbeat is not None:
            history.heartbeat = data.heartbeat
        if data.rest_count is not None:
            history.rest_count = data.rest_count
        if data.rest_level is not None:
            history.rest_level = data.rest_level
            
        s.commit()
        
    return UpdateStepHistoryResponse(
        status_code=StatusCode.SUCCESS.value,
        message="이력 정보가 수정되었습니다."
    )

def delete_step_history(data: DeleteStepHistoryRequestBody, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        stmt = delete(StepHistory).where(StepHistory.id == data.id)
        result = s.execute(stmt)
        s.commit()
        
        if result.rowcount == 0:
            return DeleteStepHistoryResponse(
                status_code=StatusCode.FAIL.value,
                message="해당 ID의 이력을 찾을 수 없습니다."
            )
            
    return DeleteStepHistoryResponse(
        status_code=StatusCode.SUCCESS.value,
        message="이력이 삭제되었습니다."
    )

def create_step_history_from_csv(csv_content: str, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    success_count = 0
    fail_count = 0
    errors = []

    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)

    with Session() as s:
        for idx, row in enumerate(rows, start=2):
            try:
                user_id = int(row.get("user_id", 0))
                start_datetime = row.get("start_datetime", "").strip()
                end_datetime = row.get("end_datetime", "").strip()
                level = int(row.get("level", 0))

                if not start_datetime or not end_datetime:
                    raise ValueError("start_datetime과 end_datetime은 필수 항목입니다.")

                start = _parse_datetime(start_datetime)
                end = _parse_datetime(end_datetime)
                duration = (end - start).seconds

                history = StepHistory(
                    user_id=user_id,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    duration=duration,
                    level=level,
                )

                rest_count_str = row.get("rest_count", "").strip()
                if rest_count_str:
                    history.rest_count = int(rest_count_str)

                rest_level_str = row.get("rest_level", "").strip()
                if rest_level_str:
                    history.rest_level = [int(x.strip()) for x in rest_level_str.split(",") if x.strip()]

                heartbeat_str = row.get("heartbeat", "").strip()
                if heartbeat_str:
                    history.heartbeat = float(heartbeat_str)

                s.add(history)
                s.commit()
                success_count += 1

            except Exception as e:
                fail_count += 1
                errors.append(f"행 {idx}: {e}")
                s.rollback()

    return CsvImportResponse(
        status_code=StatusCode.SUCCESS.value,
        message=f"CSV 등록 완료 (성공: {success_count}, 실패: {fail_count})",
        success_count=success_count,
        fail_count=fail_count,
        errors=errors,
    )
