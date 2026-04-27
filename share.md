# Dependency and Package Summary

## Project Info
- Project: `wiki-mcp`
- Python in `.venv`: `3.13.11`
- Dependency files:
  - `pyproject.toml`
  - `uv.lock`

## Runtime Dependencies (Direct, from `pyproject.toml`)
- `mcp>=1.0.0` (installed: `1.25.0`)
- `requests>=2.31.0` (installed: `2.32.5`)
- `pydantic>=2.0.0` (installed: `2.11.10`)
- `python-dotenv>=1.0.0` (installed: `1.2.1`)
- `click>=8.1.0` (installed: `8.3.1`)
- `uvicorn>=0.27.0` (installed: `0.40.0`)
- `starlette>=0.27.0` (installed: `0.50.0`)

## Development/Other Packages
- 기준: `.venv`에 설치되어 있지만 `pyproject.toml`의 직접 의존성에는 없는 패키지

```txt
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.12.1
attrs==25.4.0
authlib==1.6.6
beartype==0.22.9
cachetools==6.2.4
certifi==2026.1.4
cffi==2.0.0
charset-normalizer==3.4.4
cloudpickle==3.1.2
colorama==0.4.6
cryptography==46.0.3
cyclopts==4.4.5
diskcache==5.6.3
dnspython==2.8.0
docstring-parser==0.17.0
docutils==0.22.4
email-validator==2.3.0
exceptiongroup==1.3.1
fakeredis==2.33.0
fastapi==0.128.0
fastmcp==2.14.3
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
httpx-sse==0.4.3
idna==3.11
importlib-metadata==8.7.1
jaraco-classes==3.4.0
jaraco-context==6.1.0
jaraco-functools==4.4.0
jsonschema==4.26.0
jsonschema-path==0.3.4
jsonschema-specifications==2025.9.1
keyring==25.7.0
lupa==2.6
markdown-it-py==4.0.0
mdurl==0.1.2
more-itertools==10.8.0
openapi-pydantic==0.5.1
opentelemetry-api==1.39.1
opentelemetry-exporter-prometheus==0.60b1
opentelemetry-instrumentation==0.60b1
opentelemetry-sdk==1.39.1
opentelemetry-semantic-conventions==0.60b1
packaging==25.0
pathable==0.4.4
pathvalidate==3.3.1
platformdirs==4.5.1
prometheus-client==0.24.0
py-key-value-aio==0.3.0
py-key-value-shared==0.3.0
pycparser==2.23
pydantic-core==2.33.2
pydantic-settings==2.12.0
pydocket==0.16.6
pygments==2.19.2
pyjwt==2.10.1
pyperclip==1.11.0
python-json-logger==4.0.0
python-multipart==0.0.21
pywin32==311
pywin32-ctypes==0.2.3
pyyaml==6.0.3
redis==7.1.0
referencing==0.36.2
rich==14.2.0
rich-rst==1.3.2
rpds-py==0.30.0
shellingham==1.5.4
sortedcontainers==2.4.0
sse-starlette==3.1.2
typer==0.21.1
typing-extensions==4.15.0
typing-inspection==0.4.2
urllib3==2.6.3
websockets==16.0
-e file:///C:/Users/leeyo/programming/wiki_mcp/mcp-wiki-ver2
wrapt==1.17.3
zipp==3.23.0
```

## Full Installed Packages (`uv pip freeze`)
```txt
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.12.1
attrs==25.4.0
authlib==1.6.6
beartype==0.22.9
cachetools==6.2.4
certifi==2026.1.4
cffi==2.0.0
charset-normalizer==3.4.4
click==8.3.1
cloudpickle==3.1.2
colorama==0.4.6
cryptography==46.0.3
cyclopts==4.4.5
diskcache==5.6.3
dnspython==2.8.0
docstring-parser==0.17.0
docutils==0.22.4
email-validator==2.3.0
exceptiongroup==1.3.1
fakeredis==2.33.0
fastapi==0.128.0
fastmcp==2.14.3
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
httpx-sse==0.4.3
idna==3.11
importlib-metadata==8.7.1
jaraco-classes==3.4.0
jaraco-context==6.1.0
jaraco-functools==4.4.0
jsonschema==4.26.0
jsonschema-path==0.3.4
jsonschema-specifications==2025.9.1
keyring==25.7.0
lupa==2.6
markdown-it-py==4.0.0
mcp==1.25.0
mdurl==0.1.2
more-itertools==10.8.0
openapi-pydantic==0.5.1
opentelemetry-api==1.39.1
opentelemetry-exporter-prometheus==0.60b1
opentelemetry-instrumentation==0.60b1
opentelemetry-sdk==1.39.1
opentelemetry-semantic-conventions==0.60b1
packaging==25.0
pathable==0.4.4
pathvalidate==3.3.1
platformdirs==4.5.1
prometheus-client==0.24.0
py-key-value-aio==0.3.0
py-key-value-shared==0.3.0
pycparser==2.23
pydantic==2.11.10
pydantic-core==2.33.2
pydantic-settings==2.12.0
pydocket==0.16.6
pygments==2.19.2
pyjwt==2.10.1
pyperclip==1.11.0
python-dotenv==1.2.1
python-json-logger==4.0.0
python-multipart==0.0.21
pywin32==311
pywin32-ctypes==0.2.3
pyyaml==6.0.3
redis==7.1.0
referencing==0.36.2
requests==2.32.5
rich==14.2.0
rich-rst==1.3.2
rpds-py==0.30.0
shellingham==1.5.4
sortedcontainers==2.4.0
sse-starlette==3.1.2
starlette==0.50.0
typer==0.21.1
typing-extensions==4.15.0
typing-inspection==0.4.2
urllib3==2.6.3
uvicorn==0.40.0
websockets==16.0
-e file:///C:/Users/leeyo/programming/wiki_mcp/mcp-wiki-ver2
wrapt==1.17.3
zipp==3.23.0
```
