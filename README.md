Members -
Shane Wright
Alex Quintanilla
Aman Qais
Sheraz Rahim
Uzair Hafeez
Jorge Leon

Brief Description -
CleanRide is a web based car wash service app that allows customers to schedule appointments and customize their car wash based on the services they want. Customers can select a standard wash or add additional services like interior detailing, vacuuming, undercarriage washing, and triple foam washing. Some services, such as vacuuming or detailing, may have additional time requirements that will be incorporated into the appointment scheduling system.


Architecture
CleanRide follows a clientserver architecture with a layered structure that separates the user interface, application logic, and data storage.
1. Client Layer (Frontend)
The client layer provides the user interface through HTML and CSS. Customers can browse available car wash services, view pricing, submit booking requests, and access account related pages such as login and signup.
2. Application Layer (Backend)
The application layer is built with Django and Python. It handles HTTP requests, URL routing, form validation, user authentication, appointment management, and business logic. The application is organized into separate Django apps, including bookings, services, and customers, to keep related functionality modular and maintainable.
3. Data Layer (Database)
MongoDB is used to store application data, including customer information, saved vehicles, service details, and appointment records. The backend communicates with the database to create, retrieve, and update records as users interact with the application.
Request Flow
When a customer submits a booking form, the frontend sends the request to the Django backend. Django validates the submitted information and processes the booking, interacting with MongoDB as needed. The backend then returns a response that the frontend displays to the customer.
This architecture separates presentation, business logic, and data persistence, making CleanRide easier to maintain, test, and extend as new features are introduced.


Prototype
The CleanRide application prototype was designed using Figma. It demonstrates the planned user interface, page layouts, navigation, and customer booking experience.


Figma Prototype: https://www.figma.com/proto/Vn8Vwwh0KszgRAUkMGoyGF/Untitled?node-id=6-688&viewport=98%2C308%2C0.1&t=2LIiqzRDqfFvVQEo-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1

