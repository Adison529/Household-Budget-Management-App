import React, { useEffect, useState } from 'react';
import { Container, Button, Modal, Form, Alert, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../api';
import BudgetTile from './BudgetTile';
import '../Home.css'; // Importujemy plik CSS

function Home() {
  const [budgets, setBudgets] = useState([]);
  const [currentUser, setCurrentUser] = useState(savedUsername ? { username: savedUsername } : null);
  const [show, setShow] = useState(false);
  const [budgetName, setBudgetName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const token = localStorage.getItem('token');
  const savedUsername = localStorage.getItem('username'); // Get username from local storage

  useEffect(() => {
    if (token) {
      // Fetch current user only if not already set
      if (!currentUser) {
        api.get('/current-user/')
          .then(response => {
            setCurrentUser(response.data);
          })
          .catch(error => {
            console.error("There was an error fetching the current user!", error);
          });
      }

      // Fetch budgets
      api.get('/budget-managers/')
        .then(response => {
          setBudgets(response.data);
        })
        .catch(error => {
          console.error("There was an error fetching the budgets!", error);
        });
    }
  }, [token, currentUser]);

  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);

  const handleCreateBudget = (e) => {
    e.preventDefault();
    api.post('/budget-managers/', { name: budgetName })
      .then(response => {
        setBudgets([...budgets, response.data]);
        setBudgetName('');
        setSuccess('Budget created successfully!');
        handleClose();
      })
      .catch(error => {
        setError('There was an error creating the budget!');
        console.error("There was an error creating the budget!", error);
      });
  };

  return (
    <Container className="mt-4">
      <h2>Household Budget Management App</h2>
      {!token ? (
        <div>
          <Button variant="primary" as={Link} to="/login" className="me-2">Login</Button>
          <Button variant="secondary" as={Link} to="/register">Register</Button>
        </div>
      ) : (
        <div>
          {success && <Alert variant="success">{success}</Alert>}
          {error && <Alert variant="danger">{error}</Alert>}
          <div className="budget-grid">
            {budgets.length > 0 ? (
              budgets.map(budget => (
                <div key={budget.id} className="budget-item">
                  <BudgetTile budget={budget} currentUser={currentUser} />
                </div>
              ))
            ) : (
              <div>No budgets found.</div>
            )}
            <div className="budget-item">
              <Card style={{ width: '18rem', cursor: 'pointer' }} onClick={handleShow}>
                <Card.Body className="d-flex justify-content-center align-items-center">
                  <Card.Title>Create New Budget</Card.Title>
                </Card.Body>
              </Card>
            </div>
          </div>
        </div>
      )}

      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Budget</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleCreateBudget}>
            <Form.Group controlId="formBudgetName">
              <Form.Label>Budget Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter budget name"
                value={budgetName}
                onChange={(e) => setBudgetName(e.target.value)}
                required
              />
            </Form.Group>
            <Button variant="primary" type="submit" className="mt-3">
              Create
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
}

export default Home;
