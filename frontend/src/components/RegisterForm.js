import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function RegisterForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [captchaQuestion, setCaptchaQuestion] = useState('');
  const [captchaAnswer, setCaptchaAnswer] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();
  const [correctCaptchaAnswer, setCorrectCaptchaAnswer] = useState('');

  // Generowanie pytania CAPTCHA
  const generateCaptchaQuestion = () => {
    const num1 = Math.floor(Math.random() * 10) + 1; 
    const num2 = Math.floor(Math.random() * 10) + 1; 
    const question = `What is ${num1} + ${num2}?`;
    const answer = num1 + num2;
    setCaptchaQuestion(question);
    setCorrectCaptchaAnswer(answer.toString()); 
  };

  useEffect(() => {
    generateCaptchaQuestion();
  }, []); 

  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(password)) {
      setError('Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character, and be at least 8 characters long.');
      return;
    }

    // Verify CAPTCHA answer
    if (captchaAnswer !== correctCaptchaAnswer) {
      setError('Incorrect answer to CAPTCHA question. Please try again.');
      return;
    }

    try {
      await api.post('/register/', { username, password });
      setSuccess('Registration successful! Redirecting to login...');
      setError('');
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (error) {
      setError('There was an error registering!');
      setSuccess('');
      console.error('There was an error registering!', error);
    }

    // Generate new CAPTCHA question after registration attempt
    generateCaptchaQuestion();
  };

  return (
    <Container className="mt-4">
      <h2>Register</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}
      <Form onSubmit={handleRegister}>
        <Form.Group controlId="username">
          <Form.Label>Username</Form.Label>
          <Form.Control
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group controlId="password">
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Form.Text className="text-muted">
            Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character, and be at least 8 characters long.
          </Form.Text>
        </Form.Group>
        <Form.Group controlId="confirmPassword">
          <Form.Label>Confirm Password</Form.Label>
          <Form.Control
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group controlId="captcha">
          <Form.Label>{captchaQuestion}</Form.Label>
          <Form.Control
            type="text"
            value={captchaAnswer}
            onChange={(e) => setCaptchaAnswer(e.target.value)}
            required
          />
        </Form.Group>
        <Button variant="primary" type="submit" className="mt-3">
          Register
        </Button>
      </Form>
    </Container>
  );
}

export default RegisterForm;
