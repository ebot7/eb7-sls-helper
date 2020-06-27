FROM python:alpine3.11


RUN pip install pyyaml
RUN apk add npm
RUN npm install -g serverless
RUN npm install serverless-domain-manager serverless-manifest-plugin
RUN npm install -g newman 

COPY eb7_sls_helper/ /usr/bin/eb7_sls_helper/
ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"
# Entrypoint:
CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
