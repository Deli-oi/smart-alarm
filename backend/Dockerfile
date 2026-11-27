FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
COPY app ./app
RUN pip install --no-cache-dir .
ENV PORT=8000
EXPOSE 8000
# One process only: the scheduler runs inside the app, so more workers would double-fire jobs.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
