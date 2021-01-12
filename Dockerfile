FROM ebot7/eb7_sls_helper:test
COPY eb7_sls_helper/ /usr/bin/eb7_sls_helper/

CMD python3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
    string_output = output.decode("utf8")
