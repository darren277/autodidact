""""""
from settings import PORT, HOST, DEBUG

from main import app

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
