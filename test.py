#test.py#

from ml_classifier import predict_fire_type

result = predict_fire_type(
    brightness=350,
    confidence=95,
    frp=50,
    distance_to_industry=2
)

print(result)