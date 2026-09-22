# Prices copied from Sheraz's branch.
# Confirm these with the group before treating them as final.

services = [
    {"code": "standard-wash", "name": "Standard Car Wash", "price_cents": 2500},
    {"code": "triple-foam", "name": "Triple-Foam Wash", "price_cents": 4500},
    {"code": "undercarriage", "name": "Undercarriage Wash", "price_cents": 1500},
    {"code": "interior-detailing", "name": "Interior Detailing", "price_cents": 2000},
    {"code": "vacuum", "name": "Vacuum Service", "price_cents": 1000},
    {"code": "additional-cleaning", "name": "Additional Cleaning Services", "price_cents": 500},
]

if __name__ == "__main__":
    for service in services:
        dollars = service["price_cents"] / 100
        print(f'{service["name"]}: ${dollars:.2f}')