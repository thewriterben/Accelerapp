"""
Jenkins integration for Accelerapp.
"""

from typing import Dict, Any, List, Optional


class JenkinsIntegration:
    """
    Generates Jenkins pipelines for Accelerapp projects.
    """

    def __init__(self):
        """Initialize Jenkins integration."""
        self.pipelines: Dict[str, str] = {}

    def generate_pipeline(
        self, project_name: str, platforms: List[str], stages: Optional[List[str]] = None
    ) -> str:
        """
        Generate a Jenkins pipeline script.

        Args:
            project_name: Project name
            platforms: Target platforms
            stages: Optional custom stages

        Returns:
            Jenkinsfile content
        """
        stages = stages or ["Build", "Test", "Generate", "Deploy"]

        pipeline = f"""pipeline {{
    agent any
    
    environment {{
        PROJECT_NAME = '{project_name}'
        PYTHON_VERSION = '3.10'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Setup') {{
            steps {{
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -e .[dev]
                '''
            }}
        }}
        
        stage('Test') {{
            steps {{
                sh '''
                    . venv/bin/activate
                    pytest tests/ --junitxml=test-results.xml
                    black --check src/
                    flake8 src/
                '''
            }}
            post {{
                always {{
                    junit 'test-results.xml'
                }}
            }}
        }}
        
        stage('Generate Firmware') {{
            steps {{
                script {{
"""

        for platform in platforms:
            pipeline += f"""                    sh '''
                        . venv/bin/activate
                        accelerapp generate \\
                            --platform {platform} \\
                            --config examples/config.yaml
                    '''
"""

        pipeline += """                }
            }
        }}
        
        stage('Archive Artifacts') {{
            steps {{
                archiveArtifacts artifacts: 'output/**/*', fingerprint: true
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo 'Build succeeded!'
        }}
        failure {{
            echo 'Build failed!'
        }}
    }}
}}
"""

        return pipeline

    def generate_multibranch_pipeline(self, project_name: str) -> str:
        """
        Generate a multibranch pipeline configuration.

        Args:
            project_name: Project name

        Returns:
            Pipeline configuration
        """
        config = f"""multibranchPipelineJob('{project_name}') {{
    branchSources {{
        git {{
            remote('https://github.com/thewriterben/Accelerapp.git')
            credentialsId('github-credentials')
        }}
    }}
    
    orphanedItemStrategy {{
        discardOldItems {{
            numToKeep(10)
        }}
    }}
    
    triggers {{
        periodic(5)
    }}
}}
"""

        return config

    def generate_hardware_test_pipeline(self, platforms: List[str]) -> str:
        """
        Generate hardware testing pipeline.

        Args:
            platforms: Target hardware platforms

        Returns:
            Jenkinsfile content
        """
        pipeline = """pipeline {
    agent { label 'hardware-test-runner' }
    
    parameters {
        choice(
            name: 'PLATFORM',
            choices: [
"""

        for platform in platforms:
            pipeline += f"                '{platform}',\n"

        pipeline += """            ],
            description: 'Target hardware platform'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Generate Firmware') {
            steps {
                sh '''
                    accelerapp generate \\
                        --platform ${params.PLATFORM} \\
                        --config examples/config.yaml
                '''
            }
        }
        
        stage('Upload to Hardware') {
            steps {
                sh '''
                    python scripts/upload_firmware.py \\
                        --platform ${params.PLATFORM} \\
                        --firmware output/firmware/
                '''
            }
        }
        
        stage('Run HIL Tests') {
            steps {
                sh 'pytest tests/hil/ --platform ${params.PLATFORM}'
            }
        }
    }
}
"""

        return pipeline
