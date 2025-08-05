pipeline {
    agent any

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
        stage('installing python') {
            steps {
                sh ''' sudo apt install -y python3 python3-pip
                 python3 --version 
                pip3 --version '''
            }
        }
        stage('Running the flask app') {
              steps {
                  sh 'pip install -r requirements.txt'
                  sh 'nohup python apps.py &'
            }
        }
    
    }
}
