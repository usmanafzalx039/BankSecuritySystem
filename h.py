import json

# Load and fix transaction.json
with open('data/transaction.json', 'r') as f:
    data = json.load(f)

# Convert all IDs to strings
for tx in data:
    tx['sender'] = str(tx['sender'])
    tx['receiver'] = str(tx['receiver'])
    tx['id'] = str(tx['id'])

# Save back
with open('data/transaction.json', 'w') as f:
    json.dump(data, f, indent=4)

print("✅ Fixed transaction.json data types!")