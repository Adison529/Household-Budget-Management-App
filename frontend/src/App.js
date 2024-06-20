import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppNavbar from './components/Navbar';
import BudgetOperations from './components/BudgetList';  // Zmieniono import na BudgetOperations
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Home from './components/Home';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import { AuthProvider, AuthContext } from './AuthProvider';
import ConfirmEmail from './components/ConfirmEmail';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppNavbar />
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
};

const AppRoutes = () => {
  const { auth } = useContext(AuthContext);

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/budget-managers/:budget_manager_id/operations" element={auth.isAuthenticated ? <BudgetOperations /> : <Navigate to="/login" />} />
      <Route path="/login" element={<LoginForm />} />
      <Route path="/register" element={<RegisterForm />} />
      <Route path="/confirm-email/:uid/:token" element={<ConfirmEmail />} />
    </Routes>
  );
};

export default App;