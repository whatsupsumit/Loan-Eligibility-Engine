FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (with retry for network issues)
RUN apt-get update || true && apt-get install -y postgresql-client || true

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for uploads
RUN mkdir -p /app/media/uploads

EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
