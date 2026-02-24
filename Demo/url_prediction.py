import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import urlparse
import math
import re
import ipaddress

SUSPICIOUS_EXEC = {"exe","msi","apk","dll","bat","cmd","ps1","scr","jar","bin"}
ARCHIVE_EXT = {"zip","rar","7z","tar","gz"}
SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".bot", ".xyz", ".top", 
                   ".work", ".click", ".link", ".pw", ".cc", ".info", ".live"}

def extract_file_features(url):
    path = urlparse(url).path or ""
    name = path.split("/")[-1]
    parts = name.split(".")
    num_subdomains =  max(0, len(urlparse(url).hostname.split(".")) - 2)

    file_ext = parts[-1].lower() if len(parts) > 1 else ""
    is_executable_ext = 1 if file_ext in SUSPICIOUS_EXEC else 0
    is_archive_ext = 1 if file_ext in ARCHIVE_EXT else 0

    if name:
        raw_entropy = entropy(urlparse(url).hostname)
        filename_entropy = min(raw_entropy / 5.0, 1.0)
    else:
        filename_entropy = 0.0

    return is_executable_ext, is_archive_ext, filename_entropy, num_subdomains


def entropy(s):
    if not s:
        return 0
    p = [s.count(c)/len(s) for c in set(s)]
    return -sum(pi * math.log2(pi) for pi in p)


def check_suspicious_tld(url):
    url_lower = url.lower()
    for tld in SUSPICIOUS_TLDS:
        if tld in url_lower:
            return 1
    return 0


def is_private_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private
    except:
        return False


def is_private_ip_from_url(url):
    host = urlparse(url).hostname
    if not host:
        return False
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private
    except:
        return False


def checker(url):
    parsed = urlparse(url)
    host = parsed.hostname or ""
    host_only = host.split(":")[0]
    path = parsed.path or ""

    length_url = math.log1p(len(url))
    length_hostname = len(host)
    
    entropy_value = entropy(parsed.netloc)
    url_entropy = min(entropy_value / 5.0, 1.0)
    is_punycode = 1 if "xn--" in host else 0

    has_suspicious_tld = check_suspicious_tld(url)

    depth_of_path = len([p for p in path.split("/") if p])
    uses_https = 1 if parsed.scheme == "https" else 0

    nb_dots = url.count(".")
    nb_slash = url.count("/")
    nb_qm = url.count("?")
    nb_eq = url.count("=")

    ratio_digits_url = sum(c.isdigit() for c in url) / len(url) if len(url) else 0
    ratio_digits_host = sum(c.isdigit() for c in host) / len(host) if len(host) else 0

    prefix_suffix = 1 if "-" in host else 0

    if is_private_ip(host_only):
        ip_flag = 0
    else:
        ip_flag = 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host_only) else 0

    is_exec, is_archive, fname_entropy, num_subdomains = extract_file_features(url)

    return {
        "length_url": length_url,
        "length_hostname": length_hostname,
        "url_entropy": url_entropy,
        "is_punycode": is_punycode,
        "depth_of_path": depth_of_path,
        "num_subdomains": num_subdomains,
        "uses_https": uses_https,
        "nb_dots": nb_dots,
        "nb_slash": nb_slash,
        "nb_qm": nb_qm,
        "nb_eq": nb_eq,
        "ratio_digits_url": ratio_digits_url,
        "ratio_digits_host": ratio_digits_host,
        "prefix_suffix": prefix_suffix,
        "ip": ip_flag,
        "is_exec": is_exec,
        "is_archive": is_archive,
        "filename_entropy": fname_entropy,
        "has_suspicious_tld": has_suspicious_tld,
    }


def predict_url(url, model, FEATURES):
    
    if is_private_ip_from_url(url):
        return "🔒 - Legitimate", 0, 0.0
    
    URL_SHORTENERS = [
        'tinyurl.com', 'bit.ly', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 
        'adf.ly', 'short.link', 'rb.gy', 'cutt.ly', 'tiny.cc', 'cli.gs', 'short.io'
    ]
    url_lower = url.lower()
    
    # Extract features
    features_dict = checker(url)
    FEATURES = list(features_dict.keys())
    
    # Ensure feature order matches training set
    row = [features_dict[col] for col in FEATURES]
    
    # Reshape for model and predict
    row = np.array(row).reshape(1, -1)
    
    pred = model.predict(row)[0]
    probability = model.predict_proba(row)[0][1]
    
    # Check for URL shorteners
    for shortener in URL_SHORTENERS:
        if shortener in url_lower:
            pred, probability = 0.5, 0.5
    
    # Assign label
    if pred == 0:
        label = "Legitimate"
    elif pred == 1:
        label = "Malicious"
    elif pred == 0.5:
        label = "🔗 - UrlShortener"
    else:
        label = "Unknown"

    return label, pred, probability


def batch_urls():
    test_suite = [
    # Should be LEGITIMATE
    ("https://google.com", "LEGITIMATE"),
    ("https://mail.google.com/mail/u/0/#inbox", "LEGITIMATE"),
    ("https://github.com/microsoft/vscode", "LEGITIMATE"),
    ("https://control.sparkedhost.us/server/044674f0", "LEGITIMATE"),
    ("https://docs.google.com/document/d/1q5TlbIf8h_91VDMHj5h19xs9GBjFUceJaRjum8_wFO4/edit?tab=t.0", "LEGITIMATE"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "LEGITIMATE"),
    ("https://stackoverflow.com/questions/12345/how-to-fix", "LEGITIMATE"),
    ("https://www.geeksforgeeks.org/python/python-gui-tkinter/", "LEGITIMATE"),
    
    # Should be MALICIOUS
    ("http://182.113.2.198:48013/i", "MALICIOUS"),
    ("https://secure-paypal-verify-login.tk/update.php", "MALICIOUS"),
    ("https://mobile-bank.pages.dev/mellat.apk", "MALICIOUS"),
    ("http://182.124.207.155:59270/bin.sh", "MALICIOUS"),
    ("https://penguinpublishers.org/files/audio/meowingcybercat.mp3", "MALICIOUS"),
    ("https://motchilltv.bot/igfx.exe", "MALICIOUS"),
    ("https://docs.google.com/uc?export=download&id=1Ex0z94e1lriTzNGIYdV500FRrcVQHu7H", "MALICIOUS"),
    ("http://teslasuit.to/files//a.txt", "MALICIOUS"),
    ("http://110.36.0.103:54328/bin.sh", "MALICIOUS"),
    ("https://buckscountytaxattorney.com", "MALICIOUS")
]
    return test_suite


def features():
    sample = checker("https://www.google.com/")
    FEATURES = [
        key for key, value in sample.items()
        if isinstance(value, (int, float))
    ]
    return FEATURES

