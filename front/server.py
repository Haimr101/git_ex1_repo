from flask import Flask, request, jsonify
import requests
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

front = Flask("front_service")
CORE_URL = "http://core:5001/coreAPI"


REQUEST_COUNT = Counter(
    'front_request_count',
    'Number of requests to the front service',
    ['method', 'endpoint', 'http_status']
)
RESPONSE_TIME = Histogram(
    'front_response_time_seconds',
    'Response time for the front service',
    ['endpoint']
)

@front.route("/deposit", methods=["POST"])
def deposit():
    start_time = time.time()
    amount = request.json.get("amount", 0)
    response = requests.post(CORE_URL, json={"action": "deposit", "amount": amount})
    elapsed = time.time() - start_time
    # Record metrics
    RESPONSE_TIME.labels(endpoint='deposit').observe(elapsed)
    REQUEST_COUNT.labels(method='POST', endpoint='deposit', http_status=response.status_code).inc()
    return jsonify(response.json()), response.status_code

@front.route("/withdraw", methods=["POST"])
def withdraw():
    start_time = time.time()
    amount = request.json.get("amount", 0)
    response = requests.post(CORE_URL, json={"action": "withdraw", "amount": amount})
    elapsed = time.time() - start_time

    RESPONSE_TIME.labels(endpoint='withdraw').observe(elapsed)
    REQUEST_COUNT.labels(method='POST', endpoint='withdraw', http_status=response.status_code).inc()
    return jsonify(response.json()), response.status_code


@front.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    front.run(host="0.0.0.0", port=5000)
