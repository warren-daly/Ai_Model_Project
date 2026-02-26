# Malicious URL Detection Model

A machine learning system for detecting phishing and malware URLs using structural and behavioral analysis — no page content required.

## How to Use

1. Clone the repository:
```bash
git clone https://github.com/EspressoToastie/Ai_Model_Project
```

2. Navigate to the demo folder:
```bash
cd demo
```

3. Run the demo script:
```bash
python demo.py
```

4. Enter any URL when prompted to receive a malicious link detection confidence score.

---

## Overview

This project builds a URL classifier that identifies malicious links (phishing, malware) by analyzing URL structure, domain characteristics, and network properties.

---

## Dataset

- **Total URLs**: ~18,000
- **Malicious**: Phishing (OpenPhish, PhishTank) + Malware (URLhaus)
- **Legitimate**: Top domains (Tranco), web services (GitHub, StackOverflow, Reddit)
- **Split**: 50/50 balanced, 100% HTTPS across both classes

### Sources
| Source | Type |
|--------|------|
| [OpenPhish](https://openphish.com) | Live phishing feed |
| [PhishTank](https://phishtank.com) | Community-verified phishing |
| [URLhaus](https://urlhaus.abuse.ch) | Malware URL database |
| [Tranco](https://tranco-list.eu) | Research-based top sites |

---

## Features (18 Total)

### Structural
| Feature | Description |
|---------|-------------|
| `length_url`, `length_hostname` | URL and domain length |
| `url_entropy`, `filename_entropy` | Randomness measures |
| `nb_dots`, `nb_slash`, `nb_qm`, `nb_eq` | Special character counts |
| `ratio_digits_url`, `ratio_digits_host` | Numeric content ratio |
| `num_subdomains` | Subdomain depth |
| `depth_of_path` | URL path depth |

### Domain
| Feature | Description |
|---------|-------------|
| `ip` | IP address used instead of domain |
| `has_suspicious_tld` | Free/suspicious TLDs (`.tk`, `.ml`, etc.) |
| `prefix_suffix` | Hyphens present in domain |
| `is_punycode` | Internationalized domain encoding |

### File & Security
| Feature | Description |
|---------|-------------|
| `is_exec` | Executable file extension |
| `is_archive` | Archive file extension |
| `uses_https` | HTTPS protocol present |

---

## Model Performance

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| **KNN (k=25)** | 93.0% | 1.00 | 1.00 | 1.00 |
| XGBoost | 92.3% | 0.91 | 0.93 | 0.95 |
| Random Forest | 94.8% | 0.98 | 0.97 | 0.97 |

### Real-World Performance
- **Detection Rate**: 95% on live phishing URLs
- **False Positive Rate**: < 5%
- **Prediction Speed**: ~10–15 URLs/second

---

## Usage
```python
import joblib
from url_prediction import predict_url

# Load model
model = joblib.load('url_classifier_knn.pkl')
features = joblib.load('features_knn_final.pkl')

# Predict a URL
url = "https://suspicious-paypal-login.tk/verify"
prediction, probability = predict_url(url, model, features)

print(f"Result: {prediction} ({probability:.1%} malicious)")
```

---

## Key Findings

1. **HTTPS Balance is Critical** — Equal HTTPS distribution across classes is essential for accuracy.
2. **Structural Features Outperform Network Behavior** — URL patterns are more reliable than infrastructure signals.
3. **KNN Handles Edge Cases Well** — Nearest neighbor approach adapts well to diverse, real-world URLs.
4. **Infrastructure Features Add Noise** — Status codes and timeouts introduced false positives and were removed.

---

## Challenges & Solutions

| Challenge | Problem | Solution |
|-----------|---------|----------|
| HTTPS Imbalance | Malware URLs were only 50% HTTPS vs. 100% for legitimate | Filtered malware to HTTPS-only and rebalanced |
| False Positives | Control panels (cPanel, dashboards) flagged as malicious | Added legitimate URLs with random IDs to training data |
| Infrastructure Noise | Timeouts and DNS failures caused false positives | Removed `status_code`, `response_time`, `redirect_count` |

---

## Feature Extraction

A custom feature extraction pipeline was built to collect and structure the lexicon data used in model training.

---

## Future Improvements

- [ ] Brand impersonation detection
- [ ] URL shortener expansion
- [ ] Domain age / WHOIS data integration
- [ ] REST API deployment

---

## Ethical Considerations

All data sources are:
- ✅ Publicly available security feeds
- ✅ Used for legitimate research purposes only
- ✅ Free of private user data
- ✅ Compliant with GDPR and research ethics standards

---

## Acknowledgments

- [OpenPhish](https://openphish.com), [PhishTank](https://phishtank.com), [URLhaus](https://urlhaus.abuse.ch) — malicious URL intelligence
- [Tranco](https://tranco-list.eu) — legitimate domain rankings
- [abuse.ch](https://abuse.ch) — malware threat intelligence

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
