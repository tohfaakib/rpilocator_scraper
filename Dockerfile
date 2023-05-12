# Use the official Python image for ARM architecture (Raspberry Pi)
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the script.py file to the container
COPY script.py .

# Copy the .env file to the container
COPY .env .

# Install any necessary dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run the script.py file
CMD ["python", "script.py"]
