# Use an official Python runtime as a parent image
FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl build-essential gcc && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the server.py and requirements.txt (if exists)
COPY server.py /app/

COPY clouds.yaml /app/

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the server runs on (change if needed)
EXPOSE 8000

# Run server.py when the container launches
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
