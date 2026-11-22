class Customer:
    def __init__(self, firstName, lastName, email, phone):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phone = phone
        self.vehicle = []

    def getInfo(self):
        return f"{self.firstName} {self.lastName}, Email: {self.email}, Phone: {self.phone}"

    
