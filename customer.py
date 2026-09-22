#Created Customer class and used Copilot to generate the rest of the code 
#Adjusted the code to request username, password, and email instead of phone number and name

class Customer:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email      

#Used ChatGPT to generate the code for creating a customer and adding it to the customers list

customers = []
def create_customer():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    email = input("Enter your email: ")

    customer = Customer(username, password, email)
    customers.append(customer)

    print("Account successfully created!")
    return customer

customer = create_customer()

