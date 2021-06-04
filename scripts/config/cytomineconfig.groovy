package client.docker.config

dataSource.url='jdbc:postgresql://postgresql:5432/docker'
dataSource.username='docker'
dataSource.password='docker'

cytomine.customUI.global = [
        dashboard: ["ALL"],
        search : ["ROLE_ADMIN"],
        project: ["ALL"],
        ontology: ["ROLE_ADMIN"],
        storage : ["ROLE_USER","ROLE_ADMIN"],
        activity : ["ALL"],
        feedback : ["ROLE_USER","ROLE_ADMIN"],
        explore : ["ROLE_USER","ROLE_ADMIN"],
        admin : ["ROLE_ADMIN"],
        help : ["ALL"]
]


grails.serverURL='http://localhost-core'
grails.imageServerURL=['http://localhost-ims','http://localhost-ims2']
grails.uploadURL='http://localhost-upload'

storage_buffer='/data/images/_buffer'
storage_path='/data/images'

grails.adminPassword='c6a0aef9-ce9c-48c1-aacd-d09ed142cd3e'
grails.adminPrivateKey='806dc4fa-201b-42bf-9204-32a3015895a4'
grails.adminPublicKey='ab7838e1-7733-4bfe-9809-13ecccebe858'
grails.superAdminPrivateKey='563de51e-d78c-4e07-9589-7873bd3341be'
grails.superAdminPublicKey='4c6339f4-289a-4add-82cf-120a6a808b6f'
grails.ImageServerPrivateKey='e55cd53c-21f5-4d99-8759-a9a15f7949a1'
grails.ImageServerPublicKey='af6007fb-a20a-4722-9247-4c6d916cf699'
grails.rabbitMQPrivateKey='409aa181-2512-459e-bb86-9cde2840a94b'
grails.rabbitMQPublicKey='d6376301-eb72-4c46-b4f7-0ffcd6313ccc'

grails.notification.email='your.email@gmail.com'
grails.notification.password='passwd'
grails.notification.smtp.host='smtp.gmail.com'
grails.notification.smtp.port='587'
grails.admin.email='info@cytomine.coop'

grails.mongo.host = 'mongodb'
grails.mongo.options.connectionsPerHost=10
grails.mongo.options.threadsAllowedToBlockForConnectionMultiplier=5

grails.messageBrokerServerURL='rabbitmq:5672'

grails.serverID='86f55071-eac0-4fd4-8e3d-ecd35e775f52'
