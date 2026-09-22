class Service:
    def __init__(self, serviceName, description, price):
        self.serviceName = serviceName
        self.description = description
        self.price = price

    def get_info(self):
        return f"{self.serviceName}: {self.description} - ${self.price:.2f}"