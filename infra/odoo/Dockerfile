# Reproducible application source, independent of the nightly source in the base image.
ARG ODOO_BASE=odoo@sha256:5e755c725b3c43cf0be16d579904e1418300db3a2c44952f928eaddbcb0cc16d
FROM ${ODOO_BASE}
USER root
ARG ODOO_SOURCE_SHA=60657b50d171ddf84ab58717fdee5ac26031065b
RUN apt-get update && apt-get install -y --no-install-recommends git python3-venv build-essential libpq-dev libldap2-dev libsasl2-dev && rm -rf /var/lib/apt/lists/*
RUN git init /opt/agntia-odoo && cd /opt/agntia-odoo && git remote add origin https://github.com/odoo/odoo.git && git fetch --depth 1 origin "${ODOO_SOURCE_SHA}" && git checkout --detach FETCH_HEAD && test "$(git rev-parse HEAD)" = "${ODOO_SOURCE_SHA}" && printf '%s\n' "${ODOO_SOURCE_SHA}" > /opt/agntia-odoo-source-sha && rm -rf .git
RUN python3 -m venv --system-site-packages /opt/agntia-venv && /opt/agntia-venv/bin/pip install --no-cache-dir -r /opt/agntia-odoo/requirements.txt && ln -s /opt/agntia-odoo/odoo-bin /opt/agntia-venv/bin/odoo
ENV PATH=/opt/agntia-venv/bin:$PATH PYTHONPATH=/opt/agntia-odoo
USER odoo
