# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements.txt from the current directory
COPY requirements.txt /app/
COPY entrypoint.sh /app/
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc
# Install dependencies
RUN chmod +x /app/entrypoint.sh
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the project files
EXPOSE 8000

COPY . /app/

# Run migrations and start the server
