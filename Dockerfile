FROM python:3.8-slim

ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"
COPY eb7_sls_helper/ /usr/bin/eb7_sls_helper/
RUN pip install pyyaml boto3 tox

CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
