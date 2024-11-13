""""""
from flask import request, render_template, jsonify


#@app.route('/react_hello')
def react_hello():
    return render_template('react-response.html')



#@app.before_request
def log_request_info():
    print("AYO!")
    print(f"Received {request.method} request for {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Data: {request.data}")
    print(f"Form: {request.form}")
    #print(f"JSON: {request.json}")
    print(f"Remote Address: {request.remote_addr}")
    print(f"Remote User: {request.remote_user}")
    print(f"User Agent: {request.user_agent}")
    print(f"URL: {request.url}")
    print(f"Base URL: {request.base_url}")
    print(f"Path: {request.path}")
    print("AYO!")

#@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = jsonify({"message": "Preflight check"})
        print("Handling preflight...", response)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Cache-Control'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response, 200

#@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    #response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Cache-Control'
    response.headers['Access-Control-Allow-Headers'] = 'content-type, cache-control, accept, accept-language'
    #response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '3600'
    print("RESPONSE", response.status_code, response.headers)
    print(response.json)
    return response

#@app.after_request
def add_keep_alive_headers(response):
    #response.headers['Connection'] = 'keep-alive'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'text/event-stream'
    return response


def add_routes(app):
    app.add_url_rule('/react_hello', 'react_hello', react_hello)
    app.before_request(log_request_info)
    app.before_request(handle_preflight)
    app.after_request(add_cors_headers)
    app.after_request(add_keep_alive_headers)
    return app
