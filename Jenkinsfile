node {
    stage 'Retrieve sources'
    checkout([
        $class: 'GitSCM',
        branches: [[name: 'refs/heads/'+env.BRANCH_NAME]],
        extensions: [[$class: 'CloneOption', noTags: false, shallow: false, depth: 0, reference: '']],
        userRemoteConfigs: scm.userRemoteConfigs,
    ])

    stage 'Clean'
    sh 'rm -rf ./ci'
    sh 'mkdir -p ./ci'

    stage 'Compute version name'
    sh 'scripts/ciBuildVersion.sh ${BRANCH_NAME}'

    stage 'Download and cache dependencies'
    sh 'scripts/ciDownloadDependencies.sh'

    lock('cytomine-instance-test') {
        stage 'Run cytomine instance'
        catchError {
            sh 'docker-compose -f scripts/docker-compose.yml down -v'
        }
        sh 'docker-compose -f scripts/docker-compose.yml up -d'

        stage 'Build and test'
        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
            sh 'scripts/ciTest.sh'
        }
        stage 'Publish test'
        step([$class: 'JUnitResultArchiver', testResults: '**/ci/test-reports/*.xml'])

        stage 'Clear cytomine instance'
        catchError {
            sh 'docker-compose -f scripts/docker-compose.yml down -v'
        }
    }
}
