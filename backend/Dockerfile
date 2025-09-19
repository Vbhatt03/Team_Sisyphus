# Use an official Python runtime as a parent image (force amd64 for compatibility)
FROM --platform=linux/amd64 python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update \
	&& apt-get install -y build-essential libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY ./app /app/app

# Expose port for documentation (optional)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]