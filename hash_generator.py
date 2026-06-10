import hashlib

pin = "7094"
hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
print(hashed_pin)
