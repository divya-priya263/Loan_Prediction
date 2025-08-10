pipeline {
    agent {
        docker {
            image 'python:3.11.2'
            args '-v /var/run/docker.sock:/var/run/docker.sock --user root'
        }
    }

    stages {
        stage('Clone') {
            steps {
                echo 'Cloning repository...'
                git 'https://github.com/divya-priya263/Loan_Prediction.git'
            }
        }

        stage('Build') {
            steps {
                echo 'Building the project...'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
            }
        }

        stage('Versions') {
            steps {
                sh '''
                    python3 --version
                    pip3 --version 
                '''
            }
        }

        stage('Setup Python and Install Flask') {
            steps {
                sh '''
                 

                    # Create virtual environment in workspace
                    python3 -m venv venv

                    # Activate venv and install required packages
                    . venv/bin/activate
                    pip install flask==3.1.0 Flask-SQLAlchemy==3.1.1
                '''
            }
        }

        stage('Run Flask App') {
            steps {
                sh '''
                    # Activate venv again before running app
                    . venv/bin/activate
                    nohup python apps.py &
                '''
            }
        }


        stage('Run Flask App in Docker') {
            steps {
                sh '''
                    docker stop flask-app || true
                    docker rm flask-app || true
                    docker build -t devops-demo:latest .
                    docker run -d -p 50000:50000 --name flask-app devops-demo:latest
                '''
            }
        }
    }
}
