
login:
	docker login

build:
	docker build . -f Dockerfile.base --tag ebot7/eb7_sls_helper:test --tag eb7deploy_eb7deploy:latest

publish: login
	docker push ebot7/eb7_sls_helper:test
