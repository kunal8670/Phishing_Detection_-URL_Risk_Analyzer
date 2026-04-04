from flask import Flask, request, jsonify
from flask_cors import CORS
from services.validator import validate_url, extract_domain
from services.feature_extractor import extract_features
from services.threat_intel import check_threat_intel, init_db
from services.ml_engine import ml_engine
from services.evaluator import evaluate
from services.rate_limiter import RateLimiter
import time

app = Flask(__name__)
CORS(app)

_db_initialized = False
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


def _ensure_db():
    global _db_initialized
    if _db_initialized:
        return
    for attempt in range(10):
        try:
            init_db()
            _db_initialized = True
            return
        except Exception:
            time.sleep(2)


@app.before_request
def _lazy_init():
    _ensure_db()


@app.after_request
def add_rate_limit_headers(response):
    client_id = request.remote_addr
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.remaining(client_id))
    response.headers["X-RateLimit-Reset"] = str(
        int(time.time() + rate_limiter.reset_time(client_id))
    )
    return response


@app.route("/api/analyze", methods=["POST"])
def analyze_url():
    client_id = request.remote_addr

    if not rate_limiter.is_allowed(client_id):
        return jsonify(
            {
                "error": "Rate limit exceeded. Try again later.",
                "retry_after": int(rate_limiter.reset_time(client_id)),
            }
        ), 429

    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "URL is required"}), 400

    raw_url = data["url"]

    validated_url, error = validate_url(raw_url)
    if error:
        return jsonify({"error": error}), 400

    features = extract_features(validated_url)

    domain = extract_domain(validated_url)
    threat_result = check_threat_intel(domain)

    ml_prediction, ml_confidence = ml_engine.predict(features)

    result = evaluate(ml_prediction, ml_confidence, threat_result, features)

    return jsonify(
        {
            "url": validated_url,
            "domain": domain,
            "features": features,
            "threat_intel": threat_result,
            "ml_prediction": "phishing"
            if ml_prediction == 1
            else "legitimate"
            if ml_prediction is not None
            else "unavailable",
            "ml_confidence": round(ml_confidence, 4) if ml_confidence else None,
            "risk_score": result["final_score"],
            "risk_level": result["risk_level"],
            "breakdown": {
                "ml_score": result["ml_score"],
                "threat_score": result["threat_score"],
            },
        }
    )


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": ml_engine.model is not None})


if __name__ == "__main__":
    app.run(debug=True, port=7777)
