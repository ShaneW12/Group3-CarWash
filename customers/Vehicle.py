class Vehicle:
    def __init__(self, make, model, year, license_plate):
        self.make = make
        self.model = model
        self.year = year
        self.license_plate = license_plate

    def get_info(self):
        return f"{self.year} {self.make} {self.model} {self.license_plate}"