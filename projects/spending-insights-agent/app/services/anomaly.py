# Detects anomalous transactions using z-score within each spending category.

THRESHOLD = 1.5 
MIN_SAMPLES = 4

def compute_stats(amount:float, amounts:list[float])->float:

    if not amounts:
        return {
            "mean": 0.0,
            "variance": 0.0,
            "std": 0.0,
            "zscore": 0.0,
        }
    mean = sum(amounts) / len(amounts)
    variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
    std = variance ** 0.5
    if std == 0:
        zscore = 0.0
    else:
        zscore = (amount - mean) / std

    return {
        "mean": mean,
        "variance": variance,
        "std": std,
        "zscore": zscore,
    }


def detect_anomaly(txn:dict , category_transactions:list[dict])->dict:

    all_amounts = [t["amount"] for t in category_transactions]

 # Also ensure the txn's own amount is in the population
    if txn["amount"] not in all_amounts:
        all_amounts.append(txn["amount"])

    if len(all_amounts) < MIN_SAMPLES:
        return {
            "is_anomaly": False,
            "zscore": 0.0,
            "category_mean": 0.0,
            "category_std": 0.0,
            "reason": f"Not enough data — need {MIN_SAMPLES} in category, have {len(all_amounts)}",
        }

    stats = compute_stats(txn["amount"], all_amounts)

    zscore = stats["zscore"]
    mean = stats["mean"]
    std = stats["std"]
    is_anomaly = zscore > THRESHOLD

    return {
        "is_anomaly": is_anomaly,
        "zscore": round(zscore, 3),
        "category_mean": round(mean, 2),
        "category_std": round(std, 2),
        "reason": (
            f"Amount £{txn['amount']:.2f} is {zscore:.1f}σ above category mean £{mean:.2f}"
            if is_anomaly
            else f"Amount £{txn['amount']:.2f} is within normal range for this category"
        ),
    }

def detect_anomalies_bulk(transactions:list[dict])->list[dict]:

    by_category:dict[str,list[dict]] = {}

    for txn in transactions:
        cat = txn["category"] or "Uncategorized"
        by_category.setdefault(cat,[]).append(txn)

    results = []
    for txn in transactions:
        cat = txn.get("category") or "uncategorised"
        peers = by_category[cat]
        detail = detect_anomaly(txn, peers)
        results.append({**txn, "anomaly_detail": detail})
 
    return results
