# Use the latest official Python image from Docker Hub
FROM python:3.13-rc-alpine3.20

# Set the working directory in the container
WORKDIR /app

RUN apk --no-cache update && apk --no-cache add python3-dev \
    gcc \
    libc-dev

# Copy the current directory contents into the container at /app
COPY requirements.txt asus-exporter.py /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the Python script executable
RUN chmod +x asus-exporter.py

# Run your Python script when the container launches
CMD ["python", "./asus-exporter.py"]