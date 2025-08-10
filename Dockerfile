# Start from Jenkins LTS image
FROM jenkins/jenkins:lts

# Switch to root to install packages
USER root

# Install Docker
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*

# Install Python 3.11.2 and pip
RUN apt-get update && \
    apt-get install -y curl && \
    curl -O https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tgz && \
    tar -xvf Python-3.11.2.tgz && \
    cd Python-3.11.2 && \
    apt-get install -y build-essential libssl-dev libffi-dev zlib1g-dev && \
    ./configure && make && make install && \
    cd .. && rm -rf Python-3.11.2 Python-3.11.2.tgz

# Add Jenkins user to Docker group
RUN usermod -aG docker jenkins

# Set working directory for Python app
WORKDIR /app

# Copy Python app files
COPY . .

# Switch back to Jenkins user
USER jenkins

# Default command to run your Python app
CMD ["python3", "apps.py"]
