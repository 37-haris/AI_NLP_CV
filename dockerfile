FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv --no-cache-dir

# Copy lockfile first for better caching
COPY pyproject.toml uv.lock* ./

# Install all deps from your existing lockfile (fastest method)
RUN uv sync --frozen --no-dev

COPY . .

# Build docs
RUN uv run mkdocs build

RUN mkdir -p static/uploads

EXPOSE 8000

# Use uv run so it finds packages in the venv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]