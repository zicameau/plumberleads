FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Add debugging tools
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 