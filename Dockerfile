# Use an Alpine-based Python image
FROM python:3.11-alpine

# Install required system dependencies
RUN apk add --no-cache \
    musl-dev \
    make \
    proj \
    proj-dev \
    libffi-dev \
    openssl-dev \
    py3-numpy \
    py3-pip

# Set working directory
WORKDIR /app

# Install Python dependencies
# COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the Django application
COPY . .

# Start the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]