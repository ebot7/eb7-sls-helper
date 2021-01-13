
login:
	docker login

build:
	docker build . -f Dockerfile.base --tag ebot7/eb7_sls_helper:test --tag eb7_sls_helper:latest

publish: login
	docker push ebot7/eb7_sls_helper:test
