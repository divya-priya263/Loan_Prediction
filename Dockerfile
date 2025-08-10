# Start from Jenkins LTS
FROM jenkins/jenkins:lts

# Switch to root to install dependencies
USER root

# Install Docker and Python
RUN apt-get update && \
    apt-get install -y docker.io python3.11 python3.11-venv python3.11-distutils && \
    rm -rf /var/lib/apt/lists/*

# Add Jenkins user to Docker group
RUN usermod -aG docker jenkins

# Set working directory for Python app
WORKDIR /app

# Copy app files
COPY . .

# Switch back to Jenkins user for running Jenkins
USER jenkins

# Expose Jenkins ports
EXPOSE 8080 50000

# Start Jenkins (default CMD from base image)
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/jenkins.sh"]
