FROM ebot7/eb7_sls_helper:test

RUN yum install lapack && yum install blas-devel lapack-devel
ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"
CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
