# Malicious URL Detection Model

A machine learning system for identifying phishing and malware URLs using structural and behavioral features.

## Overview

This project develops a URL classifier that detects malicious links (phishing, malware) by analyzing URL structure, domain characteristics, and network properties—without requiring page content analysis.

## Dataset

- **Total URLs**: ~18,000
- **Malicious**: Phishing (OpenPhish, PhishTank) + Malware (URLhaus)
- **Legitimate**: Top domains (Tranco), web services (GitHub, StackOverflow, Reddit)
- **Balance**: 50/50 split, 100% HTTPS for both classes

### Data Sources
- [OpenPhish](https://openphish.com) - Live phishing feed
- [PhishTank](https://phishtank.com) - Community-verified phishing
- [URLhaus](https://urlhaus.abuse.ch) - Malware URL database
- [Tranco](https://tranco-list.eu) - Research-based top sites

## Features (18 Total)

### Structural Features
- `length_url`, `length_hostname` - URL/domain length
- `url_entropy`, `filename_entropy` - Randomness measures
- `nb_dots`, `nb_slash`, `nb_qm`, `nb_eq` - Character counts
- `ratio_digits_url`, `ratio_digits_host` - Numeric content
- `num_subdomains` - Subdomain depth
- `depth_of_path` - URL path depth

### Domain Indicators
- `ip` - IP address instead of domain
- `has_suspicious_tld` - Free/suspicious TLDs (.tk, .ml, etc.)
- `prefix_suffix` - Hyphens in domain
- `is_punycode` - International domain encoding

### File Indicators
- `is_exec` - Executable file extension
- `is_archive` - Archive file extension

### Security Indicators
- `uses_https` - HTTPS protocol

## Model Performance

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| **KNN (k=25)** | 100% | 1.00 | 1.00 | 1.00 |
| XGBoost | 92.3% | 0.97 | 0.93 | 0.95 |
| Random Forest | 97.8% | 0.98 | 0.97 | 0.97 |

### Real-World Testing
- **Detection Rate**: 95% on live phishing URLs
- **False Positive Rate**: <5%
- **Prediction Speed**: ~10-15 URLs/second

## Key Findings

1. **HTTPS Balance Critical**: Model requires equal HTTPS distribution across classes
2. **Infrastructure Features Unreliable**: Status codes, timeouts lead to false positives
3. **Structural Features Most Effective**: URL patterns more reliable than network behavior
4. **KNN Excels on Diverse Data**: Nearest neighbor approach handles edge cases better

## Usage
```python
# Load model
import joblib
model = joblib.load('url_classifier_knn.pkl')
features = joblib.load('features_knn_final.pkl')

# Predict single URL
from url_prediction import predict_url

url = "https://suspicious-paypal-login.tk/verify"
prediction, probability = predict_url(url, model, features)

print(f"Result: {prediction} ({probability:.1%} malicious)")
```


## Challenges & Solutions

### Challenge 1: HTTPS Imbalance
- **Problem**: Malware dataset 50% HTTPS, legitimate 100% HTTPS
- **Solution**: Filter malware to HTTPS-only, balance dataset

### Challenge 2: False Positives on Control Panels
- **Problem**: Control panels (cPanel, server dashboards) flagged as malicious
- **Solution**: Add legitimate URLs with random IDs to training data

### Challenge 3: Infrastructure Feature Noise
- **Problem**: Timeouts, DNS failures caused false positives
- **Solution**: Remove status_code, response_time, redirect_count features

## Future Improvements

- [ ] Implement brand impersonation checking
- [ ] Add URL shortener expansion
- [ ] Integrate domain age/WHOIS data
- [ ] Deploy as REST API service


## Ethical Considerations

All data sources are:
- ✅ Publicly available security feeds
- ✅ Used for legitimate research purposes
- ✅ No private user data collected
- ✅ Compliant with GDPR and research ethics

## License

MIT License - See LICENSE file for details

## Acknowledgments

- OpenPhish, PhishTank, URLhaus for malicious URL feeds
- Tranco for legitimate domain rankings
- abuse.ch for malware intelligence

---
