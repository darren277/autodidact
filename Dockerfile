# gunicorn sse:app --worker-class gevent --bind $(BIND_IP):$(BIND_PORT)
# Gunicorn/Flask app Dockerfile:
FROM python3.10-slim

ENV BIND_IP=
ENV BIND_PORT=

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./lib /app/lib
COPY ./utils /app/utils
COPY ./static /app/static
COPY ./templates /app/templates
COPY ./*.py /app/

EXPOSE $(BIND_PORT)

CMD ["gunicorn", "sse:app", "--worker-class", "gevent", "--bind", "$(BIND_IP):$(BIND_PORT)"]
