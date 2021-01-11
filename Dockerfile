FROM python:3.8-slim

RUN pip install pyyaml boto3 tox
RUN apt install -y curl
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt install -y nodejs git
RUN npm install -g serverless
RUN npm install serverless-domain-manager serverless-manifest-plugin
RUN npm install -g newman 

COPY eb7_sls_helper/ /usr/bin/eb7_sls_helper/
ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"


CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
