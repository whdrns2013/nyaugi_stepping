from fastapi import APIRouter, UploadFile, File
from config.config import config
from schemas.step_history import CreateStepHistoryRequestBody, CreateStepHistoryResponse, UpdateStepHistoryRequestBody, UpdateStepHistoryResponse, DeleteStepHistoryRequestBody, DeleteStepHistoryResponse, RetrieveStepHistoryResponseBody, RetrieveStepHistoryWithNameResponseBody, CsvImportResponse
from config.enums import StatusCode
from services.history_crud import create_step_history, retrieve_all_history, retrieve_history_by_user_id, update_step_history, delete_step_history, retrieve_all_history_with_user_name, retrieve_history_by_user_name, create_step_history_from_csv
from datetime import datetime

step_history_router = APIRouter(prefix=config["endpoint"]["step_history"])

@step_history_router.post(config["endpoint"]["create"], summary="계단오르기 이력 추가", response_model=CreateStepHistoryResponse)
def create_step_history_api(body:CreateStepHistoryRequestBody):
    try:
        response = create_step_history(body)
    except Exception as e:
        response = CreateStepHistoryResponse(status_code=StatusCode.FAIL.value,
                                              message=f"{e}")
    return response

@step_history_router.get(config["endpoint"]["retrieve_all"], summary="전체 이력 조회", response_model=RetrieveStepHistoryResponseBody)
def retrieve_all_history_api():
    try:
        response = retrieve_all_history()
    except Exception as e:
        response = RetrieveStepHistoryResponseBody(status_code=StatusCode.FAIL.value,
                                                  message=f"{e}",
                                                  history_list=[])
    return response

@step_history_router.get(config["endpoint"]["retrieve_by_user_id"], summary="사용자 id별 이력 조회", response_model=RetrieveStepHistoryResponseBody)
def retrieve_history_by_user_id_api(user_id: int):
    try:
        response = retrieve_history_by_user_id(user_id)
    except Exception as e:
        response = RetrieveStepHistoryResponseBody(status_code=StatusCode.FAIL.value,
                                                  message=f"{e}",
                                                  history_list=[])
    return response

@step_history_router.get(config["endpoint"]["retrieve_by_user_name"], summary="사용자 이름별 이력 조회", response_model=RetrieveStepHistoryResponseBody)
def retrieve_history_by_user_name_api(user_name: str):
    try:
        response = retrieve_history_by_user_name(user_name)
    except Exception as e:
        response = RetrieveStepHistoryResponseBody(status_code=StatusCode.FAIL.value,
                                                  message=f"{e}",
                                                  history_list=[])
    return response

@step_history_router.get(config["endpoint"]["retrieve_all_with_user_name"], summary="전체 이력 조회 with 사용자명", response_model=RetrieveStepHistoryWithNameResponseBody)
def retrieve_all_history_with_user_name_api():
    try:
        response = retrieve_all_history_with_user_name()
    except Exception as e:
        response = RetrieveStepHistoryWithNameResponseBody(status_code=StatusCode.FAIL.value,
                                                           message=f"{e}",
                                                           history_list=[])
    return response

@step_history_router.patch(config["endpoint"]["update"], summary="이력 정보 수정", response_model=UpdateStepHistoryResponse)
def update_step_history_api(body:UpdateStepHistoryRequestBody):
    try:
        response = update_step_history(body)
    except Exception as e:
        response = UpdateStepHistoryResponse(status_code=StatusCode.FAIL.value,
                                             message=f"{e}")
    return response

@step_history_router.delete(config["endpoint"]["delete"], summary="이력 삭제", response_model=DeleteStepHistoryResponse)
def delete_step_history_api(body:DeleteStepHistoryRequestBody):
    try:
        response = delete_step_history(body)
    except Exception as e:
        response = DeleteStepHistoryResponse(status_code=StatusCode.FAIL.value,
                                              message=f"{e}")
    return response

@step_history_router.post(config["endpoint"]["csv_import"], summary="CSV 파일로 이력 일괄 등록", response_model=CsvImportResponse)
def import_step_history_from_csv(file: UploadFile = File(..., description="등록할 CSV 파일")):
    try:
        content = file.file.read().decode("utf-8-sig")
        response = create_step_history_from_csv(content)
    except Exception as e:
        response = CsvImportResponse(status_code=StatusCode.FAIL.value,
                                      message=f"{e}",
                                      success_count=0,
                                      fail_count=0,
                                      errors=[str(e)])
    return response

