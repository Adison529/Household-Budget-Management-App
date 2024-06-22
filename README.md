# Household Budget Management App


## Overview 📝

Web application built with **Django** and **React.js** to help manage your household budget efficiently. Track expenses, set budgets, and gain insights into your financial health with ease. 


## Installation ⚙️

To run the application locally, please follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Adison529/Household-Budget-Management-App.git
   ```
2. Open up a terminal window, navigate into the `backend` directory, then setup and run virtual environment:

   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies for the Django backend:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the Django database and run backend server:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

5. Open up new terminal and install dependencies for the React.js frontend:

   ```bash
   cd frontend
   npm install
   ```

6. Start the React development server:

   ```bash
   npm start
   ```

6. Access the Django application in your browser at `http://localhost:8000` and the React application at `http://localhost:3000`.

## Usage 💡

Once the application is up and running, you can perform the following tasks:

- Register a new user account or log in with an existing account.
- Create household budgets or join an existing ones by sending access requests, add operations by specifying the type (income or expense), title and a person responsible for the operation.
- View summarized earnings and expenses inside the budget and gain insights into your household's economy through various graphs.

## Authors ✍️

This project is thought, planned and implemented by [Adam Słowikowski](https://github.com/Adison529) (backend) & [Miłosz Skurski](https://github.com/M1vosh) (frontend)
