FROM python:3.9.0 AS develop-stage
WORKDIR /app
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH=/app
RUN python -m venv /venv
COPY SimproToTTM/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY SimproToTTM/. .
CMD ["python", "main.py"]

FROM develop-stage as build-stage
RUN mkdir tmp
RUN apt update && apt install patchelf
COPY --from=develop-stage /venv /venv
COPY ./app /app
RUN pyinstaller -F main.py
RUN staticx /app/dist/main /app/dist/main_tmp

FROM scratch
USER 65535
COPY --from=build-stage --chown=65535:65535 /app/tmp /tmp
COPY --from=build-stage --chown=65535:65535 /app/dist/main_tmp /app/main
CMD ["/app/main"]