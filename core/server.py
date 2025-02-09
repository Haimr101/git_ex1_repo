from flask import Flask, request, jsonify
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

core = Flask("core_service")
account_balance = 0


CORE_REQUEST_COUNT = Counter(
    'core_request_count',
    'Total number of requests to the core service',
    ['method', 'endpoint', 'http_status']
)

CORE_RESPONSE_TIME = Histogram(
    'core_response_time_seconds',
    'Response time for the core service in seconds',
    ['endpoint']
)

CORE_ERROR_COUNT = Counter(
    'core_error_count',
    'Total number of error responses in the core service',
    ['endpoint']
)


@core.route("/coreAPI", methods=["POST"])
def core_api():
    start_time = time.time()  # Start timer for response time
    global account_balance
    data = request.json
    action = data.get("action")
    amount = data.get("amount", 0)
    endpoint = 'coreAPI'


    if action == "deposit":
        account_balance += amount
        response_data = {"new_balance": account_balance}
        status_code = 200

    elif action == "withdraw":
        time.sleep(5)
        if amount <= account_balance:
            account_balance -= amount
            response_data = {"message": "OK"}
            status_code = 200
        else:
            response_data = {"error": "Insufficient funds"}
            status_code = 400

    else:
        response_data = {"error": "Invalid action"}
        status_code = 400


    elapsed = time.time() - start_time


    CORE_RESPONSE_TIME.labels(endpoint=endpoint).observe(elapsed)
    CORE_REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=status_code).inc()
    if status_code >= 400:
        CORE_ERROR_COUNT.labels(endpoint=endpoint).inc()

    return jsonify(response_data), status_code



@core.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    core.run(host="0.0.0.0", port=5001)
