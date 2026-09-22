class Customers:
    def __init__(self, firstName, lastName, email, phone, password):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phone = phone
        self.password = password
        self.vehicle = None

    def getInfo(self):
        return f"{self.firstName} {self.lastName}, Email: {self.email}, Phone: {self.phone}"

    
