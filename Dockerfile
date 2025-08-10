# Use official Python image (note: no space in version)
FROM python:3.11.2

# Set working directory inside container
WORKDIR /app

# Copy all files from current directory to /app in the container
COPY . .

# Command to run your app
CMD ["python", "apps.py"]
