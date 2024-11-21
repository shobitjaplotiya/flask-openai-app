# Use the official Python slim image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files to the container
COPY . .

# Expose the port the app will run on
EXPOSE 8080

# Set the command to start the Flask app
CMD ["python", "main.py"]
