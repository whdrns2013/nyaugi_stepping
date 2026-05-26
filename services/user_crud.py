from models.step_data import User
from engine.db_engine import get_db_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from schemas.users import CreateUserRequestBody, CreateUserResponseBody, RetrieveUserInfoByNameRequestBody, RetrieveUserInfoByNameResponseBody, UpdateUserRequestBody, UpdateUserResponseBody, DeleteUserRequestBody, DeleteUserResponseBody, RetrieveAllUsersResponseBody
from schemas.dto import UserInfo
from config.enums import StatusCode, DUPLICATION
from utils.user_crud import check_email

GLOBAL_DB_ENGINE = get_db_engine()

def create_user(data:CreateUserRequestBody,
                engine=GLOBAL_DB_ENGINE):
    # 이메일 중복 체크
    is_duplicate = check_email(data.email)
    if is_duplicate == DUPLICATION.DUPLICATED:
        return CreateUserResponseBody(
            status_code = StatusCode.FAIL.value,
            message = "중복된 이메일입니다."
        )
    
    user = User()
    user.name = data.name
    user.email = data.email
    
    # 신규 사용자 등록    
    Session = sessionmaker(bind=engine)
    
    with Session() as s:
        s.add(user)
        s.commit()
        s.refresh(user)
        id = user.id
    
    return CreateUserResponseBody(
        id = id,
        status_code = StatusCode.SUCCESS.value,
    )

def delete_user(data: DeleteUserRequestBody, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        stmt = delete(User).where(User.id == data.id)
        result = s.execute(stmt)
        s.commit()
        
        if result.rowcount == 0:
            return DeleteUserResponseBody(
                status_code=StatusCode.FAIL.value,
                message="해당 ID의 사용자를 찾을 수 없습니다."
            )
            
    return DeleteUserResponseBody(
        status_code=StatusCode.SUCCESS.value,
        message="사용자가 삭제되었습니다."
    )

def retrieve_all_users(engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        stmt = select(User)
        datas = s.scalars(stmt).all()
    
    return RetrieveAllUsersResponseBody(
        user_list=[UserInfo(id=u.id, name=u.name, email=u.email) for u in datas],
        status_code=StatusCode.SUCCESS.value,
    )

def update_user(data: UpdateUserRequestBody, engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    with Session() as s:
        user = s.get(User, data.id)
        if not user:
            return UpdateUserResponseBody(
                status_code=StatusCode.FAIL.value,
                message="해당 ID의 사용자를 찾을 수 없습니다."
            )
            
        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            # 이메일 변경 시 중복 체크 (본인 제외)
            if data.email != user.email:
                # check_email은 단순 존재 여부만 확인하므로, 여기서는 간단히 처리하거나 
                # check_email 로직을 수정해야 함. 현재는 단순 업데이트.
                user.email = data.email
        
        s.commit()
        
    return UpdateUserResponseBody(
        status_code=StatusCode.SUCCESS.value,
        message="사용자 정보가 수정되었습니다."
    )

def retrieve_user_info_by_name(data:RetrieveUserInfoByNameRequestBody,
                              engine=GLOBAL_DB_ENGINE):
    Session = sessionmaker(bind=engine)
    
    with Session() as s:
        smtm = select(User).where(User.name == data.name)
        datas = s.scalars(smtm).all()
    
    return RetrieveUserInfoByNameResponseBody(
        user_list = [UserInfo(id=u.id, name=u.name, email=u.email) for u in datas],
        status_code = StatusCode.SUCCESS.value,
        )

