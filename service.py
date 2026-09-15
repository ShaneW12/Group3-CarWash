class Service:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return self.name + " - $" + str(self.price)


standard_wash = Service("Standard Car Wash", 25)
triple_foam = Service("Triple-Foam Wash", 45)
undercarriage = Service("Undercarriage Wash", 15)
interior_detailing = Service("Interior Detailing", 20)
vacuum = Service("Vacuum Service", 10)
additional_cleaning = Service("Additional Cleaning Services", 5)


def calculate_total(services):
    total = 0

    for service in services:
        total += service.price

    return total