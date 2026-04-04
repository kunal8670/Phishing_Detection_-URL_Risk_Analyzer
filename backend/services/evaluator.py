def evaluate(ml_prediction, ml_confidence, threat_result, features):
    ml_score = 0
    threat_score = 0

    if ml_prediction is not None:
        if ml_prediction == 1:
            ml_score = ml_confidence * 100
        else:
            ml_score = (1 - ml_confidence) * 100
    else:
        ml_score = None

    if threat_result["found"]:
        threat_score = 100
    else:
        threat_score = 0

    if ml_score is not None:
        final_score = round(ml_score * 0.4 + threat_score * 0.6, 2)
    else:
        final_score = round(float(threat_score), 2)

    if final_score <= 25:
        risk_level = "Safe"
    elif final_score <= 50:
        risk_level = "Suspicious"
    elif final_score <= 75:
        risk_level = "Warning"
    else:
        risk_level = "Risky"

    if threat_result["found"]:
        risk_level = "Risky"

    return {
        "ml_score": ml_score,
        "threat_score": threat_score,
        "final_score": final_score,
        "risk_level": risk_level,
    }
