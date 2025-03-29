# backend/Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

RUN apt-get update && apt-get install -y curl

# Install dependencies
COPY requirements.txt .
RUN pip install --cache-dir=/tmp/pip_cache -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 3300

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3300"]