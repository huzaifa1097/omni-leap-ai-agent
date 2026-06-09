FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY ./app /code/app
COPY ./main.py /code/main.py

# Secrets (firebase-service-account.json, credentials.json, token.json) are
# loaded at runtime from Google Secret Manager via secrets_service.py and
# must NOT be baked into the image.

EXPOSE 8080

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
