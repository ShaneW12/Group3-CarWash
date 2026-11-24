# CleanRide – Car Wash Appointment Management System

## Team Members

- Shane Wright
- Alex Quintanilla
- Aman Qais
- Sheraz Rahim
- Uzair Hafeez
- Jorge Leon

## Project Description

CleanRide is a web-based car wash appointment management application that allows customers to schedule appointments, manage their vehicles, and customize their car wash experience by selecting the services they need.

Customers can choose a standard car wash or additional services such as interior detailing, vacuuming, undercarriage washing, and triple foam washing.

The application dynamically calculates service prices, estimated appointment durations, and available booking times based on customer selections and existing appointments.

CleanRide also features an optional AI-powered appointment recommendation assistant integrated with Google's Gemini Large Language Model (LLM). The assistant helps customers select an available appointment time by analyzing their selected services, total appointment duration, and available booking slots.

The application uses Django and Python for backend functionality, HTML, CSS, and JavaScript for the frontend, and MongoDB Atlas for data storage.

---

## Architecture

CleanRide follows a client-server architecture with a layered structure that separates the user interface, application logic, and data storage.

### 1. Client Layer (Frontend)

The frontend is developed using HTML, CSS, JavaScript, and Django templates.

It allows customers to:

- Browse available car wash services and pricing.
- Register and log into customer accounts.
- Add, edit, and delete saved vehicles.
- Select multiple services during appointment booking.
- View dynamically calculated appointment prices and durations.
- Select from dynamically generated available appointment times.
- Receive optional AI-powered appointment recommendations.
- Review appointment summaries before confirming bookings.
- View and cancel existing appointments.

JavaScript is used to update appointment information dynamically without requiring customers to refresh the entire page.

### 2. Application Layer (Backend)

The backend is developed using Django and Python.

It handles:

- HTTP requests and URL routing.
- Customer registration and authentication.
- Vehicle management.
- Appointment creation and cancellation.
- Service and pricing calculations.
- Appointment duration calculations.
- Appointment availability validation.
- Google Gemini API integration.
- Business logic and database interactions.

The application is divided into multiple Django apps, including:

- `bookings` – Appointment scheduling, availability, and AI recommendations.
- `customers` – Customer accounts and saved vehicle management.
- `services` – Car wash service information, prices, and durations.

Separating these components improves code organization, maintainability, and testing.

### 3. Data Layer (Database)

CleanRide uses MongoDB Atlas as its database.

MongoDB stores application information including:

- Customer accounts and profile information.
- Saved customer vehicles.
- Available car wash services.
- Service prices and durations.
- Appointment information.
- Appointment status and scheduling details.

Django communicates with MongoDB using the MongoDB backend to retrieve, create, and update application records.

### 4. AI Integration Layer

CleanRide integrates Google's Gemini LLM using the `google-genai` Python SDK.

The AI assistant is an optional feature that recommends appointment times based on information provided by the application's scheduling engine.

The integration includes:

- `bookings/ai_scheduler.py` – Communicates with Google's Gemini API, processes recommendations, and validates AI responses.
- `bookings/scheduling.py` – Uses deterministic Python logic to calculate valid appointment availability.
- `prompts/scheduling_v1.txt` – Stores the versioned instructions provided to the Gemini model.

**The AI does not calculate appointment availability, determine service durations, or create appointments.**

These responsibilities remain with the application's Python backend.

Gemini only recommends a time from the list of available appointment slots provided by the Python scheduling engine.

This separation ensures that customers cannot book unavailable appointment times simply because an AI model recommended them.

---

## Request Flow

When a customer submits an appointment request:

1. The frontend collects the customer's selected vehicle, services, date, and appointment time.
2. Django retrieves the selected services from MongoDB.
3. Python calculates the total service price and estimated appointment duration.
4. The scheduling engine determines available appointment slots.
5. JavaScript displays the available appointment times to the customer.
6. Optionally, the customer can request an AI recommendation.
7. Gemini receives the selected services, calculated duration, and available appointment slots.
8. Gemini returns a recommended appointment time and an explanation.
9. The application validates that the recommended time exists in the available slots.
10. The customer can accept the recommendation or manually select another available time.
11. Django validates the final booking request before saving the appointment to MongoDB.

This architecture ensures that the core appointment system remains functional independently of the Gemini API.

---

## Completed Features

### 1. Customer Registration

Customers can create an account by providing personal information and login credentials.

Registration includes input validation and checks to prevent duplicate accounts.

### 2. Customer Login

Registered customers can securely log in using their email and password.

Authentication allows customers to access account-specific features, including saved vehicles and appointment history.

### 3. My Vehicles – Vehicle Management

A new **My Vehicles** section was added for registered customers.

Logged-in customers can:

- Save vehicles to their accounts.
- View previously saved vehicles.
- Edit vehicle information.
- Delete vehicles that are no longer needed.
- Select saved vehicles when booking appointments.

This eliminates the need to repeatedly enter vehicle information for every appointment.

Vehicle records are stored in MongoDB and associated with the appropriate customer account.

### 4. Simplified Booking for Logged-In Customers

The booking process was improved for authenticated users.

When logged in, customers no longer need to manually reenter their contact information during each booking.

Instead, CleanRide automatically retrieves the customer's saved account information.

Logged-in customers can also select a previously saved vehicle rather than entering vehicle details again.

Guest customers can continue entering their information manually.

This improves convenience and reduces repetitive data entry.

### 5. Dynamic Service Catalog and Pricing

CleanRide now dynamically retrieves available car wash services from MongoDB.

Customers can select multiple services during a single appointment.

Each service includes:

- Service name.
- Service price.
- Estimated service duration.

When customers select or remove services, JavaScript automatically recalculates the total appointment price.

Prices are stored as integer cents and displayed in dollars to support accurate pricing calculations.

### 6. Dynamic Appointment Duration

Appointment duration is calculated automatically based on the services selected.

Each service has an estimated duration stored in MongoDB.

Python calculates the total appointment duration by adding the durations of all selected services.

JavaScript displays the updated estimated duration in the booking summary.

This calculated duration is also used by the appointment scheduling engine to determine which appointment times can accommodate the requested services.

### 7. Dynamic Appointment Availability

CleanRide includes a Python-based appointment availability system.

The system determines available appointment times based on:

- The customer's selected date.
- The total duration of the selected services.
- Existing scheduled appointments.
- Scheduling rules defined in the Python backend.

Available times are retrieved dynamically using Django endpoints and JavaScript.

The application validates appointment availability again when the customer submits the booking form.

This prevents the application from relying solely on frontend availability information.

### 8. Dynamic Appointment Summary

A new appointment summary was implemented using JavaScript in `booking.js`.

The summary updates automatically when customers select or remove services.

It displays:

- Selected car wash services.
- Total estimated appointment duration.
- Total appointment price.

This allows customers to review the services they selected and the expected cost before submitting their appointment.

### 9. Google Gemini LLM Appointment Assistant

CleanRide now includes an AI-powered appointment recommendation feature using Google's Gemini LLM.

The assistant allows customers to request an appointment time recommendation based on their selected services and current appointment availability.

The AI receives:

- Appointment date.
- Selected services.
- Total calculated appointment duration.
- Available appointment starting times.

Gemini returns a structured JSON response containing:

- `recommended_time` – The recommended appointment starting time.
- `reason` – An explanation of the recommendation.

The application validates the recommended time against the available appointment slots generated by Python.

Customers can click **Use This Time** to populate the appointment time dropdown with the AI's suggestion.

The customer must still submit the appointment form to create a booking.

The AI recommendation feature is optional and does not replace the regular appointment scheduling system.

If the Gemini API is unavailable, customers can still book appointments manually.

### 10. Appointment Management

Customers can review their scheduled appointments through the My Appointments section.

The application supports appointment cancellation and stores appointment statuses in MongoDB.

---

## Prototype

The CleanRide application prototype was designed using Figma.

The prototype demonstrates the planned user interface, page layouts, navigation, and customer booking experience.

**Figma Prototype:**

[View CleanRide Figma Prototype](https://www.figma.com/proto/Vn8Vwwh0KszgRAUkMGoyGF/Untitled?node-id=6-688&viewport=98%2C308%2C0.1&t=2LIiqzRDqfFvVQEo-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1)

---

## CI/CD Pipeline

CleanRide uses GitHub Actions to automate its continuous integration and continuous delivery workflow.

The workflow is located at:

`.github/workflows/csc325_ci_cd.yml`

The pipeline is configured to run when code is pushed to or pull requests target the `main` branch.

### Pipeline Stages

**1. Setup**

Prepares the GitHub Actions environment, checks out the project repository, and configures the required runtime.

**2. Dependencies**

Installs the project's required Python dependencies, including Django, MongoDB integration packages, and the Google Gemini SDK (`google-genai`).

**3. Testing**

Runs Django system checks and automated tests to identify application errors before changes are merged.

**4. Deploy**

Executes the project's configured deployment stage after the required preceding stages complete successfully.

The workflow helps the development team detect errors early and maintain code quality throughout development.

### GitHub Secrets and API Security

Following the implementation of Google Gemini, the team updated its GitHub Actions configuration to include the Gemini API key as a repository secret.

The application accesses the key using the `GEMINI_API_KEY` environment variable.

This allows the key to be supplied to authorized workflows without exposing it in source code.

Sensitive credentials are stored separately from the application's tracked source files.

The `.env` file should remain excluded from Git tracking through `.gitignore`.

---

## Agile Development and Project Management

CleanRide uses Agile development practices and GitHub Projects to organize project tasks.

The development team uses:

- Epics to represent larger features.
- User stories to describe functionality from the customer's perspective.
- Sub-issues to organize smaller development tasks.
- A Kanban board to monitor progress.
- Sprints to organize and review development work.
- Pull requests and code reviews to manage changes.

The team's Kanban board includes:

- Backlog
- To Do
- In Progress
- Ready for Review
- Done

### Feature Epics

**Service Catalog and Price Management**

Covers the implementation of the dynamic service catalog, service selection, pricing calculations, duration calculations, and appointment summary.

**AI-Powered Appointment Recommendations**

Covers integration of the Google Gemini LLM, AI recommendation generation, validation of recommended appointment times, and integration with the booking interface.

### AI-Assisted User Story Creation

The team used ChatGPT to help draft and organize user stories and sub-issues for selected GitHub Project epics.

AI-generated suggestions were used to help describe requirements, define acceptance criteria, and organize development tasks.

The development team remained responsible for reviewing the generated stories and implementing the functionality.

---

## Artificial Intelligence Usage and Disclosure

**AI tools were used during the development of CleanRide. This section documents the assistance received, including successful contributions, incorrect recommendations, troubleshooting, code generation, and documentation updates.**

### 1. ChatGPT – Google Gemini LLM Integration

ChatGPT was used to assist with integrating Google's Gemini API into the CleanRide application.

It helped the team understand how to connect a Python/Django application to a Google Gemini LLM and how to structure the appointment recommendation functionality.

ChatGPT provided guidance and code examples for implementing the AI integration using the Google Gen AI Python SDK.

### 2. ChatGPT – Incorrect Gemini Model Recommendation

During development, ChatGPT initially recommended a Gemini model that did not work with the project's API access.

The initial implementation attempted to use `gemini-2.5-flash`, which returned a `404 NOT_FOUND` error indicating that the model was no longer available to new users.

ChatGPT subsequently suggested `gemini-3.8-flash`, which returned a `503 UNAVAILABLE` error because the model was experiencing high demand.

After additional troubleshooting and testing, the team successfully generated recommendations using `gemini-3.5-flash-lite`.

**This process demonstrated that AI-generated technical recommendations are not always correct or immediately usable.** The team had to test the suggested models, review error messages, and adjust the implementation before achieving a working integration.

### 3. ChatGPT – AI Scheduling Code and Prompt Development

ChatGPT assisted with developing and updating the following files:

- `bookings/ai_scheduler.py`
- `prompts/scheduling_v1.txt`
- `bookings/views.py`
- `bookings/urls.py`
- `static/js/booking.js`
- `booking.html`

The assistance included generating code examples, explaining API integration steps, creating AI prompt instructions, validating structured JSON responses, and integrating the AI feature into the existing booking interface.

ChatGPT also assisted with connecting the AI recommendation system to appointment times generated by the Python scheduling engine.

The team reviewed, modified, and tested the generated code within the application.

### 4. ChatGPT – Dynamic Pricing and Appointment Functionality

ChatGPT was used to assist with implementation and troubleshooting of dynamic appointment features.

This included support for:

- Dynamic service pricing.
- Appointment duration calculations.
- Service selection and booking summaries.
- Dynamic appointment availability.
- JavaScript integration with Django endpoints.
- Troubleshooting frontend and backend errors.

The final application uses Python to validate appointment availability and pricing information.

### 5. ChatGPT – CI/CD Pipeline Assistance

ChatGPT assisted with creating and troubleshooting the GitHub Actions CI/CD workflow.

Following integration of the Gemini SDK, GitHub Actions initially failed because the workflow environment did not have the required `google-genai` package installed.

ChatGPT helped identify the missing dependency and provided guidance for updating the project's dependency configuration.

The team also configured GitHub Secrets to support secure access to the Gemini API key.

### 6. ChatGPT – Agile Project Documentation

ChatGPT was used to generate and refine user stories for GitHub Project epics.

This included stories relating to:

- AI-powered appointment recommendations.
- Dynamic service pricing.
- Appointment duration calculations.
- Appointment summaries.
- AI error handling.
- Future customer appointment preferences.

These AI-generated stories were intended to support Agile planning, sprint organization, and project documentation.

### 7. ChatGPT – README Documentation Update

**This README.md file was updated and expanded with assistance from OpenAI's ChatGPT.**

The development team supplied the original README content and requested an updated version documenting the application's recently implemented features.

ChatGPT assisted with rewriting, formatting, organizing, and expanding the documentation.

This included descriptions of the application architecture, dynamic pricing, vehicle management, appointment scheduling, Gemini LLM integration, CI/CD changes, Agile planning, and AI usage disclosures.

The team is responsible for reviewing the AI-generated documentation to ensure it accurately reflects the implemented application.

### 8. Google Gemini – Runtime AI Assistant

In addition to using ChatGPT during development, CleanRide uses Google's Gemini LLM as part of its running application.

Gemini generates optional appointment time recommendations and explanations based on available appointment information provided by the backend.

Gemini does not independently determine appointment availability, calculate service prices, or create customer bookings.

All final appointment validation and database operations remain under the control of the Django/Python application.

### AI Usage Summary

AI tools assisted with brainstorming, code generation, implementation guidance, debugging, Agile documentation, and README development.

The development team remained responsible for integrating the generated code, reviewing results, correcting errors, testing functionality, and managing the final application.

---

## Future Improvements

Potential future improvements to CleanRide include:

- Allowing customers to specify appointment preferences when requesting AI recommendations.
- Displaying appointment preference options only after customers choose to use the AI assistant.
- Improving AI recommendations based on customer-selected preferences.
- Expanding automated tests for the Gemini integration.
- Further improvements to the booking interface and vehicle management experience.

---

## Conclusion

CleanRide provides a customizable car wash booking experience through a combination of Django, Python, MongoDB Atlas, JavaScript, and Google Gemini AI.

The application now supports dynamic service pricing, automatic appointment duration calculations, real-time appointment availability calculations, saved vehicle management, simplified bookings for logged-in customers, and optional AI-powered appointment recommendations.

The project also demonstrates the practical use of Agile development methods, GitHub Actions CI/CD, API integration, and responsible AI-assisted software development.

AI tools played a supporting role throughout development, while the development team maintained responsibility for implementing, validating, and maintaining the final application.