from datetime import datetime
from flask import Flask, request, jsonify, render_template
from errors import validation_error
import logic
from models import Frequency
import logging
import os


def index():
    return render_template('index.html')


def api_pay_peroids_remaining():
    start_date = request.args.get('start_date', None)
    frequency = request.args.get('frequency', None)
    if not all([start_date, frequency]):
        return validation_error('All fields are required')
    try:
        start_date = datetime.strptime(start_date, '%m/%d/%Y')
    except ValueError:
        return validation_error('Invalid date')
    if not frequency in Frequency:
        return validation_error('Invalid frequency')
    return jsonify({'pay_periods_remaining':
                    logic.pay_periods_remaining(start_date, frequency)})


def init_urls(app):
    app.add_url_rule('/', 'index', index, methods=['GET'])
    app.add_url_rule(
        '/api/pay_periods_remaining',
        'api_pay_peroids_remaining',
        api_pay_peroids_remaining, methods=['GET'])


def init_logging(app):
    if not app.debug:
        logdir = os.getenv('OPENSHIFT_DIY_LOG_DIR', '/tmp')
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            os.path.join(logdir, 'api.log'), maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)


def init_application(static_url_path=None, static_folder=None):
    if static_url_path and static_folder:
        app = Flask(
            __name__,
            static_url_path=static_url_path,
            static_folder=static_folder)
    else:
        app = Flask(__name__)
    init_urls(app)
    init_logging(app)
    return app

if __name__ == '__main__':
    app = init_application(
        static_url_path='/static',
        static_folder='../client/public')
    app.run(
        debug=True,
        port=8002)
