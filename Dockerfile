FROM ebot7/eb7_sls_helper:test


ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/"
CMD pytho3 /usr/bin/eb7_sls_helper/src/gh_action_interface.py
