#!/usr/bin/env python3
import os
from flask import Flask
from flask import request, send_from_directory, url_for
import csv
import config # diverse configurable variables
import SqlWrapper # jasper's sql functions for communication with the DB without sqlAlchemy

# set up server directory for web
STATIC_DIR = 'static'
STATIC_DIR_WITH_SLASH = "/{}".format(STATIC_DIR)
# set up global server variable and global database variable, based on environment variables
FLASK_SERVER = Flask(__name__, static_url_path=STATIC_DIR_WITH_SLASH, static_folder=STATIC_DIR)
DB_URL = os.environ.get("RUNTIME_POSTGRES_DB_SERVER")
DB_PORT = os.environ.get("RUNTIME_POSTGRES_DB_PORT")
DB_NAME = os.environ.get("RUNTIME_POSTGRES_DB_NAME")
DB_USER = os.environ.get("RUNTIME_POSTGRES_DB_USER")
DB_PW = os.environ.get("RUNTIME_POSTGRES_DB_PW")
FLASK_SERVER.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PW, DB_URL, DB_PORT, DB_NAME)
DEBUG_VERSION = "h"

def main():
    FLASK_SERVER.run('0.0.0.0', port=80)
    
# Server Routes: ---------------------------------------------------------

# Sample to receive GET request and argument /?name=asdf
@FLASK_SERVER.route('/', methods=["GET"])
def heloworld():
    name = request.args.get('name', default = 'Josi', type = str)
    return "{} Helo {}".format(DEBUG_VERSION, name)

# Sample to receive post request
@FLASK_SERVER.route('/post', methods=["POST"])
def helopost():
    return "post response {}".format(str(request.form))

# Sample to route file that is called differently (but not for static)
# @FLASK_SERVER.route('/static/content')
# def sample_route():
#    return send_from_directory(STATIC_DIR, 'messages_typora.html')


@FLASK_SERVER.route('/loadDebugCSV')
def loadDebugCSV():
    out=""
    # read whole initialization file into one string
    with open(config.SQL_INITIALIZATION_FILE, 'r') as content_file:
        sqlFile = content_file.read()
    #try:
        #SqlWrapper.InitializeDatabase(sqlFile, 
         #       DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    #except:
    #    out+="ree!<br/><br/>"
    # parse CSV
    csvData = parseDebugCSV()
    # tell database about csv content
    out += dbInitializeTeachingAssistants(csvData)
    # add version
    version = DEBUG_VERSION
    return "{}<br/><br/>csvData: {}\<br/><br/>Out:{}".format(version, str(csvData), str(out))

# CSV Logic: --------------------------------------------------------------

"""
return: a list of OrderedDictionaries with the keys config.CSV_TA_NETHZ and CSV_TA_NETHZ
"""
def parseCSV(csvFile):
    with open(csvFile, 'r') as f:
        reader = csv.DictReader(f)
        mylist = [line for line in reader]
        print(mylist)
        # use config.CSV_TA_NETHZ and config.CSV_LECTURE_NAME
    return mylist

def parseDebugCSV():
    return parseCSV('./debug_inputs/inputs.csv')

def dbInitializeTeachingAssistants(csvData):
    returnString = ""
    # TODO: do for all data
    try:
        returnString += "{0},{1},{2},{3},{4},{5} <br/>".format(csvData[0][config.CSV_TA_NETHZ], DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
        SqlWrapper.MakeAssistant(csvData[0][config.CSV_TA_NETHZ],
            DB_NAME, DB_USER, DB_PW, DB_URL, DB_PORT)
    except Exception as e:
        returnString+=str(e)
    return returnString


if __name__ == '__main__':
    main()
