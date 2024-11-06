include .env

g:
	gunicorn sse:app --worker-class gevent --bind $(BIND_IP):$(BIND_PORT)

w:
	waitress-serve --listen=*:$(BIND_PORT) wsgi:app
