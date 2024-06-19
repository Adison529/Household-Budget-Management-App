# Household Budget Management App


## Overview 📝

Web application built with **Django** and **React.js** to help manage your household budget efficiently. Track expenses, set budgets, and gain insights into your financial health with ease. 


## Installation ⚙️

To run the application locally, please follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Adison529/Household-Budget-Management-App.git
   ```
2. Setup and run virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies for the Django backend:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the Django database and run backend server:

   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

5. Install dependencies for the React.js frontend in new terminal, make sure that you have your virtual environment running:

   ```bash
   cd frontend
   npm install
   ```

6. Start the development server:

   ```bash
   npm start
   ```

6. Access the application in your browser at `http://localhost:3000`.

## Usage 💡

Once the application is up and running, you can perform the following tasks:

- Register a new user account or log in with an existing account.
- Create budgets or join existing ones by sending request access, set operations by specifying the type (income or expense), give them a title and choose a person responsible for the operation.
- View summarized earnings and expenses inside the budget.

## Authors ✍️

This project is thought, planned and implemented by [Adam Słowikowski](https://github.com/Adison529) (backend) & [Miłosz Skurski](https://github.com/M1vosh) (frontend)
