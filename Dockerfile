# Dockerfile
# Task 2: Containerize the data analysis app

FROM python:3.11-slim

# Avoid .pyc files + enable clean logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project
COPY . /app

# Default command runs Task 1 analysis (local CSV expected in /app/data/All_Diets.csv)
CMD ["python", "data_analysis.py"]
