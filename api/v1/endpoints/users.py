from fastapi import APIRouter
from config.config import config
from schemas.users import CreateUserRequestBody, CreateUserResponseBody, RetrieveUserInfoByNameRequestBody, RetrieveUserInfoByNameResponseBody, UpdateUserRequestBody, UpdateUserResponseBody, DeleteUserRequestBody, DeleteUserResponseBody, RetrieveAllUsersResponseBody
from config.enums import StatusCode
from services.user_crud import create_user, retrieve_user_info_by_name, retrieve_all_users, update_user, delete_user
from datetime import datetime

users_router = APIRouter(prefix=config["endpoint"]["users"])

@users_router.post(config["endpoint"]["create"], summary="사용자 추가", response_model=CreateUserResponseBody)
def create_user_api(body:CreateUserRequestBody):
    try:
        response = create_user(body)
    except Exception as e:
        response = CreateUserResponseBody(status_code=StatusCode.FAIL.value,
                                          message=f"{e}")
    return response

@users_router.post(config["endpoint"]["retrieve_user_info_by_name"], summary="이름으로 사용자 정보 검색", response_model=RetrieveUserInfoByNameResponseBody)
def retrieve_user_info_by_user_name(body:RetrieveUserInfoByNameRequestBody):
    try:
        response = retrieve_user_info_by_name(body)
    except Exception as e:
        response = RetrieveUserInfoByNameResponseBody(status_code=StatusCode.FAIL.value,
                                                       message=f"{e}")
    return response

@users_router.get(config["endpoint"]["retrieve_all"], summary="전체 사용자 조회", response_model=RetrieveAllUsersResponseBody)
def retrieve_all_users_api():
    try:
        response = retrieve_all_users()
    except Exception as e:
        response = RetrieveAllUsersResponseBody(status_code=StatusCode.FAIL.value,
                                                message=f"{e}",
                                                user_list=[])
    return response

@users_router.patch(config["endpoint"]["update"], summary="사용자 정보 수정", response_model=UpdateUserResponseBody)
def update_user_api(body:UpdateUserRequestBody):
    try:
        response = update_user(body)
    except Exception as e:
        response = UpdateUserResponseBody(status_code=StatusCode.FAIL.value,
                                           message=f"{e}")
    return response

@users_router.delete(config["endpoint"]["delete"], summary="사용자 삭제", response_model=DeleteUserResponseBody)
def delete_user_api(body:DeleteUserRequestBody):
    try:
        response = delete_user(body)
    except Exception as e:
        response = DeleteUserResponseBody(status_code=StatusCode.FAIL.value,
                                          message=f"{e}")
    return response
