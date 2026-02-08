ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.0.2
FROM ${BUILD_FROM}

RUN apk add --no-cache nodejs npm

WORKDIR /opt/web
COPY web /opt/web
RUN npm install && npm run build

RUN mkdir -p /app/static && cp -r /opt/web/dist/* /app/static/

WORKDIR /app
COPY backend /app/backend

RUN pip install --no-cache-dir fastapi uvicorn[standard] aiohttp pydantic pydantic-settings

EXPOSE 8099
CMD ["/usr/local/bin/python", "-m", "backend.main"]
