ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache nodejs npm python3 py3-pip

WORKDIR /opt/web
COPY web /opt/web
RUN npm install && npm run build

RUN mkdir -p /app/static && cp -r /opt/web/dist/* /app/static/

WORKDIR /app
COPY backend /app/backend

RUN pip3 install --no-cache-dir fastapi uvicorn[standard] aiohttp pydantic pydantic-settings

EXPOSE 8099
CMD ["/usr/local/bin/python", "-m", "backend.main"]
