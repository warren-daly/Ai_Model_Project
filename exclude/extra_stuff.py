url = "https://www.google.com"
label, pred, probability = await predict_url(url, model_xgb, FEATURES)

print(url)
print(f"{label} | {probability * 100:.1f}%") # → 0(legit) or 1(malicious)
print("Weights of Url for prediction.")
features = await run_checker(url)
from pprint import pprint
pprint(features)


# Debugging during Batches and Urls

import logging
import sys

logger = logging.getLogger("checker")
logger.setLevel(logging.INFO)  # or Debug

logger.handlers.clear()

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.propagate = False

