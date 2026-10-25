FROM node:24-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY backend/data ./data
COPY --from=frontend /app/frontend/dist /app/frontend/dist
ENV PORT=8000
EXPOSE 8000
# Shell form so the host-assigned $PORT (Heroku) is expanded at startup.
CMD uvicorn app.server:app --host 0.0.0.0 --port $PORT
