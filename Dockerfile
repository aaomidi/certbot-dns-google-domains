FROM python:3.10 AS build

WORKDIR /opt/certbot/plugin

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN ~/.local/bin/poetry config virtualenvs.create false

# Build plugin
COPY [".", "."]
RUN ~/.local/bin/poetry build


#################################

FROM certbot/certbot

COPY --from=build /opt/certbot/plugin/dist/*.whl /opt/certbot/src/plugin/
RUN python tools/pip_install.py --no-cache-dir /opt/certbot/src/plugin/*.whl

ENTRYPOINT ["/usr/bin/env"]
