## Service  

### 시작  

```bash
uv run streamlit run app_streamlit.py
```


## Alembic  

### 데이터모델 마이그레이션  

- 데이터모델 수정 후 리비전 생성  

```bash
uv run alembic revision --autogenerate -m "리비전 메시지"
```

- 데이터모델을 DB에 반영  

```bash
uv run alembic upgrade head
```

- 데이터모델 다운그레이드

```bash
uv run alembic downgrade a1b2c3d4e5f6
```

### 최초 Alembic 세팅  

- Alembic 초기화  

```bash
uv run alembic init alembic
```

- `alembic.ini` 에 연결할 DB URL 입력  

```bash
...
sqlalchemy.url = mysql+pymysql://user:password@host:port/db
...
```

- `alembic/env.py` 에 마이그레이션 할 데이터모델 메타데이터 불러오기  

```python
from models import Base
target_metadata = Base.metadata
```