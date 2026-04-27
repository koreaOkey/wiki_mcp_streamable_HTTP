# [git_sop 대비 변경] 단일 app.py/uvicorn 실행 대신,
# 패키지로 설치된 wiki-mcp CLI를 실행하도록 구성.
FROM default-route-openshift-image-registry.apps.ocpdev.shinhan.com/gap-cagent-dev/gaf-base-serving-py312:0.0.3

ARG NEXUS_URL_HOST
ARG NEXUS_URL
ARG SHBMCP_SERVER_NAME

ENV PIP_TRUSTED_HOST=$NEXUS_URL_HOST
ENV PIP_INDEX_URL=$NEXUS_URL
ENV SHBMCP_SERVER_NAME=$SHBMCP_SERVER_NAME

WORKDIR /app

# [git_sop 대비 변경] pyproject + src 패키지 구조를 복사.
COPY pyproject.toml /app/pyproject.toml
COPY src /app/src

# [git_sop 대비 변경] requirements.txt 대신 프로젝트 자체를 설치.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
# [git_sop 대비 변경] wiki-mcp 기본 실행 환경값.
ENV MCP_TRANSPORT=streamable
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8002
ENV CONFLUENCE_PROTOCOL=http
ENV CONFLUENCE_HOST=
ENV CONFLUENCE_PORT=8090
ENV CONFLUENCE_PERSONAL_TOKEN=
ENV CONFLUENCE_SSL_VERIFY=true

# [git_sop 대비 변경] wiki-mcp 기본 포트 8002 노출.
EXPOSE 8002

# [git_sop 대비 변경] pyproject의 CLI 엔트리포인트 실행.
ENTRYPOINT ["wiki-mcp"]
