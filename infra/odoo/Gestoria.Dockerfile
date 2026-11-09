FROM python:3.12-slim-bookworm
ARG APP_UID=1000
RUN useradd --uid ${APP_UID} --create-home app
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY agntia_gestoria ./agntia_gestoria
RUN pip install --no-cache-dir . && mkdir /data && chown app:app /data
USER app
EXPOSE 8010
CMD ["agntia-gestoria","--host","0.0.0.0","--port","8010"]
