FROM python:3.12-slim

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app


# Install Postgres connector
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POSTGRESQL_CFLAGS="-I/usr/include/postgresql"
ENV POSTGRESQL_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lpq"
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install psycopg2

# Copy the application code
COPY ./lib ./lib
COPY ./models ./models
COPY ./routes ./routes
COPY ./utils ./utils
COPY ./static ./static
COPY ./templates ./templates
COPY ./settings.py .
COPY ./database.py .
COPY ./manage.py .
COPY ./logger.py .
COPY ./main.py .
COPY ./wsgi.py .

EXPOSE 5000

RUN pip install gunicorn

CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:app"]
