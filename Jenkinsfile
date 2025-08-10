pipeline {
    agent {
        docker {
            image 'python:3.11.2'
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
    
        stage('versions') {
            steps {
                sh """ 
                    python3 --version
                    pip3 --version 
                """
            }
        }
            
        stage('Running the flask app') {
              steps {

                  sh ' pip install flask3.1.0'
                  sh ' pip install Flask-SQLAlchemy3.1.1'
                  sh 'nohup python apps.py &'
            }
        }
        stage('Run Flask App in Docker') {
              steps {
                  sh '''
                  docker stop flask-app || true
                  docker rm flask-app || true
                  docker run -d -p 50000:50000 --name flask-app devops-demo:latest
                  '''
            }
      }
    }
}
