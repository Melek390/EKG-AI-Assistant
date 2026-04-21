# test_ecg.py
from LMMintegration.ecgassistant import generate_ecg_interpretation

result = generate_ecg_interpretation(
    image_path="path/to/ecg.png",
    age="65",
    history="HTA",
    symptoms="Douleur thoracique + dyspnée"
)

print(result)