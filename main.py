from fastapi import FastAPI
from api.v1.router import router
from config.config import config
# from utils.logger.default_logger import logger
import os
import platform
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title=config["service"]["title"],
    version=config["service"]["version"],
    docs_url=None # 커스텀 swagger 적용
)

def init_db():
    import os
    db_path = config["db"]["file_path"]
    if not os.path.exists(db_path):
        from models import Base
        from sqlalchemy import create_engine
        engine = create_engine(config["db"]["url"])
        Base.metadata.create_all(bind=engine)

# swagger 설정
app.mount("/static/swagger", StaticFiles(directory="static/swagger/"), name="swagger")
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )

app.include_router(router)

def run_with_gunicorn_uvicorn():
    # Linux, Unix 계열 환경에서는 gunicorn 설치 가능
    # logger.debug(f"Start App :: run with gunicorn and uvicorn")
    command = [
        "gunicorn",
        "main:app",
        "--bind", f"{str(config["service"]["bind"])}:{config["service"]["port"]}",
        "--workers", str(config["service"]["worker_num"]),
        "--worker-class", "uvicorn.workers.UvicornWorker"
    ]
    try:
        os.execvp("gunicorn", command)
    except Exception as e:
        # logger.error(e)
        print(e)

def run_with_uvicorn():
    # Windows 환경에서는 gunicorn 설치 불가 : uvicorn만 실행
    # logger.debug(f"Start App :: run with uvicorn")
    import uvicorn
    uvicorn.run('main:app',
                host=str(config["service"]["bind"]),
                port=int(config["service"]["port"]),
                workers=int(config["service"]["worker_num"]) if config["service"]["mode"] == "prod" else 1,
                reload=True
                )

if __name__ == '__main__':
    # logger.debug("===== RUN SERVICE =====")
    print("===== RUN SERVICE =====")
    # db 초기화
    if not os.path.exists(config["db"]["file_path"]):
        init_db()
    # fastapi 가동
    if platform.system() == "Windows":
        run_with_uvicorn()
    else:
        run_with_gunicorn_uvicorn()

