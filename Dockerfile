# Use official Python
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt update && apt install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000 for Django server
EXPOSE 8000

# Default command (development)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
