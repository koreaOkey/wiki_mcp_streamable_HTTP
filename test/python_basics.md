# Python 기초 개념 정리

## 1. 모듈 (Module)
- `.py` 파일 하나 = 모듈
- 여러 모듈이 모여 하나의 패키지(폴더)를 구성
- 여러 모듈이 역할을 분담해서 하나의 서버를 구성

```
wiki_mcp_fastmcp/        ← 패키지
  __main__.py            ← 진입점
  __init__.py            ← CLI 정의
  server.py              ← 서버 로직
  api_client.py          ← 클라이언트 로직
  models.py              ← 데이터 모델
```

---

## 2. import

`from test import add` 를 실행하면 Python이 하는 일:

1. `test.py` 파일을 **위에서 아래로 전부 읽고 실행**
2. 그 결과로 만들어진 이름들(`add`, `subtract`) 중에서 `add`만 가져옴

즉 import = **파일 전체를 한 번 실행해서 메모리에 올려두는 것**

```python
from test import add   # test.py 전체 실행 후 add만 가져옴
```

---

## 3. import 캐싱

Python은 한 번 import한 모듈을 `sys.modules`에 캐시해둔다.

```python
import test   # test.py 실행 (처음만)
import test   # 캐시에서 바로 가져옴 (두 번째부터 거의 0ms)
```

같은 파일을 여러 곳에서 import해도 **딱 한 번만 실행**된다.

| 상황 | 속도 영향 |
|------|----------|
| 함수 정의만 있는 파일 | 거의 없음 |
| numpy, pandas 같은 대형 라이브러리 | 처음 실행 시 수백ms |
| DB 연결, 네트워크 요청 포함 | 느릴 수 있음 |
| 두 번째 import | 항상 빠름 (캐시) |

---

## 4. `if __name__ == "__main__"`

import할 때 실행되면 안 되는 코드를 이 블록 안에 넣는다.

| 상황 | `__name__` 값 |
|------|--------------|
| `python test.py` 직접 실행 | `"__main__"` → 블록 실행됨 |
| `from test import add` (import) | `"test"` → 블록 실행 안 됨 |

```python
def add(a, b):
    return a + b

if __name__ == "__main__":
    assert add(1, 2) == 3   # 직접 실행할 때만 동작
```

---

## 5. python 인터프리터

`python` = Python 인터프리터를 실행해라

```
내가 쓴 코드 (Python)
      ↓
  python (인터프리터가 한 줄씩 읽고 번역)
      ↓
  컴퓨터가 실행
```

| | 비유 |
|--|------|
| `.py` 파일 | 한국어로 쓴 요리 레시피 |
| `python` | 한국어 → 기계어 통역사 |
| 컴퓨터 | 통역된 내용을 실제로 실행 |

---

## 6. `python -m` 명령어

`-m` = 모듈 모드로 실행

| `-m` 뒤에 오는 것 | 실행되는 것 |
|---|---|
| 파일 (`my_script`) | `my_script.py` |
| 패키지 (`wiki_mcp_fastmcp`) | `wiki_mcp_fastmcp/__main__.py` |

```bash
python -m wiki_mcp_fastmcp
# wiki_mcp_fastmcp/__main__.py 를 찾아서 실행
```

`__main__.py` 가 없는 패키지에 `-m` 을 쓰면 에러:
```
No module named wiki_mcp_fastmcp.__main__; 'wiki_mcp_fastmcp' is a package
```

---

## 7. MCP 서버 실행 흐름

```
python -m wiki_mcp_fastmcp
        ↓
__main__.py  → main() 호출
        ↓
__init__.py  → Click CLI, create_mcp_server() 호출
        ↓
server.py    → FastMCP 서버 생성, Tool 등록
        ↓
mcp.run()    → HTTP 서버 시작 (포트 8002), 무한 대기
```

---

## 8. python -m vs Docker

| | python -m | Docker |
|--|-----------|--------|
| 비유 | 내 주방에서 요리 | 레시피+재료 담긴 도시락 박스 |
| 환경 | 내 PC 그대로 | 완전히 격리된 환경 |
| 이식성 | 낮음 | 높음 |
| 설정 | 내 PC에 직접 설치 필요 | Dockerfile만 있으면 됨 |
| 코드 동작 | 동일 | 동일 |

코드 동작 자체는 동일하고, **어디서, 어떤 환경에서 실행하느냐**의 차이.

---

## 9. 용어 정리

| 용어 | 의미 |
|------|------|
| 모듈 | `.py` 파일 하나 |
| 패키지 | 모듈들이 모인 폴더 |
| 서버 | 요청을 받아서 응답하는 프로그램 |
| 서비스 | Docker 등으로 배포/운영 중인 서버 |
| 인터프리터 | Python 코드를 기계어로 번역하는 프로그램 |
| 진입점(entrypoint) | 프로그램이 시작되는 파일 (`__main__.py`) |