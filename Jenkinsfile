pipeline {
    agent any

    environment {
        REPO = 'KTB-Hackathon/ai'
        DOCKER_HUB_REPO = 'jonum12312/ktbhackai'  
        DOCKER_HUB_CREDENTIALS_ID = 'dockerhub' 
        PINECONE_API_KEY = credentials('PINECONE_API_KEY')
        UPSTAGE_API_KEY = credentials('UPSTAGE_API_KEY')
        OPENAI_API_KEY = credentials('OPENAI_API_KEY')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "https://github.com/${REPO}.git"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Jenkins에 저장된 Docker Hub 자격 증명 사용
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_HUB_CREDENTIALS_ID}") {
                        dockerImage.push('latest')  // 태그를 'latest'로 푸시
                        dockerImage.push("${BUILD_NUMBER}")  // 빌드 번호로도 태그를 푸시
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // 로컬 서버에서 기존 컨테이너 제거
                    sh "docker rm -f ktbhackai || true"

                    // Docker Hub에서 최신 이미지 pull
                    sh "docker pull ${DOCKER_HUB_REPO}:latest"

                    // 컨테이너 실행 (로컬 포트 80 -> 컨테이너 8080)
                    sh "docker run -d --name ktbhackai -e OPENAI_API_KEY=${OPENAI_API_KEY} -e PINECONE_API_KEY=${PINECONE_API_KEY} -e UPSTAGE_API_KEY=${UPSTAGE_API_KEY} -p 7777:80 ${DOCKER_HUB_REPO}:latest"
                }
            }
        }
    }
}
