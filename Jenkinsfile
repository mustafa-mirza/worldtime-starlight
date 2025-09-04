pipeline {
    agent any
    environment {
        ARTIFACTORY_URL = 'http://192.168.103.145:8081/artifactory'
        REPOSITORY_NAME = '001'
    }
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
                    def firstUrl = 'http://192.168.103.101:30008'
		    //def firstUrl = 'http://192.168.103.101:30010'
                    sh "curl -sS $firstUrl"
                }
            }
        }

         stage('Generate Report'){
            steps{
                script{
                 //   sh 'python3 reportGenerator.py --fromdate "2025-05-01 00:00:01" --domain 7741_FinCorp --subdomain QA3 --reportType application_model_architecture'
		    sh 'python3 reportGenerator.py --fromdate "2025-05-01 00:00:01" --domain 7741_FinCorp --subdomain QA3 --reportType application_model_architecture_and_threat'
		    sh 'python3 reportGenerator.py --fromdate "2025-05-01 00:00:01" --domain 7741_FinCorp --subdomain QA3 --reportType vulnerabilities_stride_long --format pdf'
		    sh 'python3 reportGenerator.py --fromdate "2024-02-05 11:00:00" --todate "2025-02-06 23:00:00" --domain 661_FedTrust --subdomain UAT3 --reportType application_model_threat_dragon --templateName Fedtrust_Template_20241018'
                    // sh 'python3 reportGenerator.py --fromdate "2024-04-20 00:00:01" --domain k8s --subdomain dev_applications --reportType application_model_threat_dragon_plus'
		//    sh 'python3 reportGenerator.py --fromdate "2024-06-09 11:00:00" --todate "2024-06-10 23:00:00" --domain k8s --subdomain dev_applications --reportType application_model_threat_dragon --templateName k8s_sentinel3 --metadataFilter "PR:0834e79e-baa6"'
		    //sh 'python3 reportGenerator.py --fromdate "2024-05-31 11:00:00" --todate "2024-05-31 23:00:00" --domain k8s --subdomain dev_applications --reportType application_model_threat_dragon --templateName k8s_sentinel3 --metadataFilter "PR:c3ad83f1-7097"'
                }
            }
        }
               
        stage('Upload Threat Files') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: '2c5b3acf-5069-41d3-9de0-32f760f9ee21',
                        usernameVariable: 'ARTIFACTORY_USER',
                        passwordVariable: 'ARTIFACTORY_API_KEY'
                    )]) {
                        // Upload AAM files
                        sh """
                            if ls App_model_Architecture_And_Threat_*UTC.zip >/dev/null 2>&1; then
                                echo "📁 Found Threat files:"
                                ls -la App_model_Architecture_And_Threat_*UTC.zip
                                
                                for file in App_model_Architecture_And_Threat_*UTC.zip; do
                                    echo "📤 Uploading: \$file"
                                    
                                    # Construct URL properly with double quotes
                                    UPLOAD_URL="${env.ARTIFACTORY_URL}/${env.REPOSITORY_NAME}/\$file"
                                    echo "🔗 Target URL: \$UPLOAD_URL"
                                    
                                    if curl -f -v \\
                                           -u"\${ARTIFACTORY_USER}:\${ARTIFACTORY_API_KEY}" \\
                                           -T "\$file" \\
                                           "\$UPLOAD_URL"; then
                                        echo "✅ Successfully uploaded: \$file"
                                    else
                                        echo "❌ Failed to upload: \$file"
                                        exit 1
                                    fi
                                done
                            else
                                echo "❌ No files matching pattern 'App_model_Architecture_And_Threat_*UTC.zip' found!"
                                exit 1
                            fi
                        """
                    }
                }
            }
        }
    
	// Add more stages as needed
    }
}
