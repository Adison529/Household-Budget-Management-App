import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppNavbar from './components/Navbar';
import BudgetOperations from './components/BudgetList';  // Zmieniono import na BudgetOperations
import ExpenseList from './components/ExpenseList';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Home from './components/Home';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const token = localStorage.getItem('token');

  return (
    <Router>
      <div className="App">
        <AppNavbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/budget-managers/:budget_manager_id/operations" element={token ? <BudgetOperations /> : <Navigate to="/login" />} />
          <Route path="/expenses" element={token ? <ExpenseList /> : <Navigate to="/login" />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
