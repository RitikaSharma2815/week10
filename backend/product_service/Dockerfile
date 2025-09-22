# backend/product_service/Dockerfile

FROM python:3.11-slim

# System deps (psycopg2 needs libpq)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps
COPY requirements.txt /app/requirements.txt
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir fastapi uvicorn psycopg2-binary requests sqlalchemy pydantic aio-pika azure-storage-blob; \
    fi

# Copy service code
COPY . /app

# Ensure Python can import the "app" package
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    POSTGRES_HOST=db \
    POSTGRES_DB=products \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

EXPOSE 8000

# IMPORTANT: module path is app.main:app (because your code is under /app/app/main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
