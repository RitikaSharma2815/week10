# backend/product_service/Dockerfile

FROM python:3.11-slim

# System deps (psycopg2 needs libpq)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# If you have requirements.txt, use it; otherwise install essentials
COPY requirements.txt /app/requirements.txt
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir fastapi uvicorn psycopg2-binary requests; \
    fi

# Copy the rest of the service
COPY . /app

# Default envs (compose will override)
ENV POSTGRES_HOST=db \
    POSTGRES_DB=products \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Run via uvicorn listening on 0.0.0.0 (compose can override this command if needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
