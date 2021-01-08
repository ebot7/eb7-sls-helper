FROM ebot7/eb7_sls_helper:test

RUN apk --no-cache add musl-dev linux-headers g++

ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"
CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
