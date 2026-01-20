# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.10-alpine AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, copy the rest of the project source code and install it
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Remove unnecessary files from the virtual environment before copying
RUN find /app/.venv -name '__pycache__' -type d -exec rm -rf {} + && \
    find /app/.venv -name '*.pyc' -delete && \
    find /app/.venv -name '*.pyo' -delete && \
    echo "Cleaned up .venv"

# Final stage
FROM python:3.10-alpine

# Create a non-root user 'app'
RUN adduser -D -h /home/app -s /bin/sh app
WORKDIR /app
USER app

COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Disable Python output buffering for proper logging
ENV PYTHONUNBUFFERED=1

# 환경 변수 기본값 설정 (실행 시 덮어쓰기 가능)
# MCP 서버 설정
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8002

# Confluence 설정 (IP와 포트 분리)
ENV CONFLUENCE_PROTOCOL=http
ENV CONFLUENCE_HOST=localhost
ENV CONFLUENCE_PORT=8090
ENV CONFLUENCE_PERSONAL_TOKEN=""
ENV CONFLUENCE_SSL_VERIFY=true

# Expose SSE port
EXPOSE 8002

# Run wiki-mcp (환경 변수를 자동으로 읽음)
ENTRYPOINT ["wiki-mcp"]
