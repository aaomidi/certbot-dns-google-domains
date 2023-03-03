# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
