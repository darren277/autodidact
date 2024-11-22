include .env

g:
	gunicorn sse:app --worker-class gevent --bind $(BIND_IP):$(BIND_PORT)

w:
	waitress-serve --listen=*:$(BIND_PORT) wsgi:app

w2:
	waitress-serve --host=127.0.0.1 --port=8000 --asyncore-loop-timeout=3600 --connection-limit=100 wsgi:app
