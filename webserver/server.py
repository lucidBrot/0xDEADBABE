#!/usr/bin/env python3
from flask import Flask
from flask import request, send_from_directory, url_for

STATIC_DIR = 'static'
STATIC_DIR_WITH_SLASH = "/{}".format(STATIC_DIR)
FLASK_SERVER = Flask(__name__, static_url_path=STATIC_DIR_WITH_SLASH, static_folder=STATIC_DIR)

def main():
    FLASK_SERVER.run('0.0.0.0', port=80)
    
# Sample to receive GET request and argument /?name=asdf
@FLASK_SERVER.route('/', methods=["GET"])
def heloworld():
    name = request.args.get('name', default = 'Josi', type = str)
    return "Helo {}".format(name)

# Sample to receive post request
@FLASK_SERVER.route('/post', methods=["POST"])
def helopost():
    return "post response {}".format(str(request.form))

# Sample to route file that is called differently (but not for static)
# @FLASK_SERVER.route('/static/content')
# def sample_route():
#    return send_from_directory(STATIC_DIR, 'messages_typora.html')

if __name__ == '__main__':
    main()
