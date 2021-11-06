import time
from flaskr.controllers.home import home_bp
from flask import current_app, render_template, request, json, Response, jsonify, current_app as app
import logging
import os
from werkzeug.utils import secure_filename
import boto3
from flask import Flask, render_template
from flask_sse import sse
from google.cloud import pubsub_v1
from libs.redis_custom import redis_client, pubsub

client = boto3.client('s3')

ALLOWED_EXTENSIONS = {'mp4', 'wav'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@home_bp.before_app_request
def before_request():
    pass


@home_bp.route('/', methods=['GET'])
def index():
    data = {
        "env": os.getenv("FLASK_ENV")
    }
    return render_template('index.html', data=data)


@home_bp.route('/upload', methods=['GET'])
def file_upload():
    data = {
        "env": os.getenv("FLASK_ENV")
    }
    return render_template('file_upload.html', data=data)


@home_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            "success": 0,
            "msg": "No file uploaded"
        }), 400
    file = request.files['file']
    file_binary = file.read()
    if file.filename == '':
        return jsonify({
            "success": 0,
            "msg": "No file uploaded"
        }), 400
    file_id = str(int(time.time()))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        client.put_object(Body=file_binary, Bucket='subhajit-temp-can-delete', Key='Temp/' + filename, ACL='public-read')
        pub_sub_data = {
            "file": 'Temp/' + filename,
            "bucket": "subhajit-temp-can-delete",
            "file_id": file_id
        }
        redis_client.publish('file-convert-channel', json.dumps({"data": pub_sub_data}))
    else:
        return jsonify({
            "success": 0,
            "msg": "No file uploaded"
        }), 400
    return jsonify({
        "success": 1,
        "msg": "File uploaded",
        "data": {
            "file_id": file_id
        }
    }), 200


@home_bp.route('/subscriber', methods=['POST', "GET"])
def subscriber():
    body = (request.get_json(force=True))
    attributes = body["message"]["attributes"]
    file_name = attributes.get("filename")
    bucket = attributes.get("location")
    file_id = attributes.get("file_id")

    return jsonify({
        "success": 1,
        "msg": "File uploaded"
    }), 200
