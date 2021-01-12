# eb7-sls-helper
![coverage badge](coverage.svg "Test coverage")
![Integration Test](https://github.com/ebot7/eb7-sls-helper/workflows/Integration%20Test/badge.svg?branch=master)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=eb7-sls-helper&metric=alert_status&token=b1dabb8807aefb70db33acf7b25b4eb85ed8aefc)](https://sonarcloud.io/dashboard?id=eb7-sls-helper)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=eb7-sls-helper&metric=bugs&token=b1dabb8807aefb70db33acf7b25b4eb85ed8aefc)](https://sonarcloud.io/dashboard?id=eb7-sls-helper)

This tool makes validating (to come), deployment and removal of serverless services easy for CI/CD.

## How to update the pipeline tool.

Since 06/11, we've introduced a image that's pre-built in our docker hub registry:

`https://hub.docker.com/repository/docker/ebot7/eb7_sls_helper`

Whenever we have a new code merged/created here, we need to build/update this container so that the workflow picks up the changes.

For this, I've created a simple Makefile to build, tag and publish the images. In order to use this, you need the credentials from ebot7 docker hub account. You can ask around for the credentials, so someone with permissions can share them with you (ask Ilya [[@il-bot](https://github.com/il-bot)] to share them through LastPass). Once you have the credentials do a quick:

`docker login`

Enter the ebot7 username and password that you've received. 

That's it! Now you can publish the new image!

To build and tag, run:

`make build`

To push image, run:

`make publish`

