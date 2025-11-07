import logging
from flask import jsonify


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def success_response(data=None, message="Success"):
    response = {
        "status": "success",
        "message": message,
        "data": data or {}
    }

    return jsonify(response)


def error_response(message="An error occurred", status_code=400):
    logging.error(message)
    response = {
        "status": "error",
        "message": message
    }

    return jsonify(response), status_code