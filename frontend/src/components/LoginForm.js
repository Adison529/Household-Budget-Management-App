import React, { useState, useContext } from 'react';
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { AuthContext } from '../AuthProvider';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { setAuth } = useContext(AuthContext);

  const handleLogin = (e) => {
    e.preventDefault();
    api.post('/login/', { username, password })
      .then(response => {
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('username', username);
        setAuth({
          isAuthenticated: true,
          token: response.data.access,
          username: username
        });
        navigate('/');
      })
      .catch(error => {
        console.error("There was an error logging in!", error);
        setError("Invalid username or password");
      });
  };

  return (
    <Container className="mt-4">
      <h2>Login</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleLogin}>
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
        </Form.Group>
        <Button variant="primary" type="submit" className="mt-3">
          Login
        </Button>
      </Form>
    </Container>
  );
}

export default LoginForm;
