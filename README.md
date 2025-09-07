Internship Placement Manager
This project is a backend application designed to help schools manage their internship programs. It keeps track of important information for students, employers, mentors, and the internship placements themselves. The goal is to make it simpler to organize and oversee all internship-related data.

Key Features
Student Management: Create and update student profiles with their personal details and major.

Employer and Mentor Tracking: Keep a clear record of companies and mentors, as well as their internship listings.

Placement Matching: Easily link a student to a specific internship and mentor for each placement.

Evaluation System: A way to add and view performance evaluations for each internship.

Getting Started
Prerequisites
To run this project, you only need to have Docker installed on your computer. This tool handles all the other dependencies and sets up the application and database for you.

How to Run the App
Navigate to the main project folder in your terminal.

Run the following command to start the application:

docker-compose up --build

Once the containers are running, you can check that the application is working by opening your web browser and going to http://localhost:8000/docs. You should see the interactive API documentation page.

Technologies Used
FastAPI: The web framework used to build the application's API.

PostgreSQL: The database used to store all the project data.

Docker: Used to package and run the application and database together.