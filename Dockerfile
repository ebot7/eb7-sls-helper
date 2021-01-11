FROM ebot7/eb7_sls_helper:test

RUN apk --no-cache add musl-dev linux-headers g++ gcc python3-dev libffi-dev openssl-dev

ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"
COPY eb7_sls_helper/ /usr/bin/eb7_sls_helper/
RUN pip install pytest pytest-cov xlrd moto

CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
