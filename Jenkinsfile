pipeline {
    agent any
    tools{
        maven 'mvn3.9.6'
    }
    stages{
        stage('Build Maven'){
            steps{
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/mustafa-mirza/worldtime-starlight']]])
                sh 'mvn clean install'
            }
        }
        stage('Build docker image'){
            steps{
                script{
                    sh 'docker build -t mustafamirza/worldtime .'
                }
            }
        }
        stage('Push image to Hub'){
            steps{
                script{
                   withCredentials([string(credentialsId: 'dockerhub-pwd', variable: 'dockerhubpwd')]) {
                   sh 'docker login -u mustafamirza -p ${dockerhubpwd}'

}
                   sh 'docker push mustafamirza/worldtime'
                }
            }
        }
        stage('Deploy to k8s'){
            steps{
                script{
                    kubernetesDeploy (configs: 'deploymentservice.yaml',kubeconfigId: 'k8s01config')
                    sleep(time: 60, unit: "SECONDS")
                }
            }
        }
        
        stage('Access First URL') {
            steps {
                script {
                    def firstUrl = 'http://192.168.103.101:30009'
                    sh "curl -sS $firstUrl"
                }
            }
        }

         stage('Generate Report'){
            steps{
                script{
                    sh 'python3 reportGenerator.py --fromdate "2024-03-23 00:00:01" --domain k8s --subdomain dev_applications --reportType application_model_architecture'
                   // sh 'python3 reportGenerator.py --fromdate "2024-02-23 00:00:01" --domain k8s --subdomain dev_applications --reportType application_model_threat_dragon_plus'
		    sh 'python3 reportGenerator.py --fromdate '2024-03-28 00:00:01' --domain k8s --subdomain dev_applications --reportType application_model_threat_dragon_plus --templateName ACME-Template'
                }
            }
        }
	// Add more stages as needed
    }
}
