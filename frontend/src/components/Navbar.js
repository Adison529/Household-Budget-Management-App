import React, { useState } from 'react';
import { Navbar, Nav, Container, Button, Modal, Form, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';

function AppNavbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [showAccessRequestModal, setShowAccessRequestModal] = useState(false);
  const [uniqueId, setUniqueId] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleShowLogout = () => setShowLogoutModal(true);
  const handleCloseLogout = () => setShowLogoutModal(false);

  const handleShowAccessRequest = () => setShowAccessRequestModal(true);
  const handleCloseAccessRequest = () => setShowAccessRequestModal(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    handleCloseLogout();
    navigate('/login');
  };

  const handleSendAccessRequest = async (e) => {
    e.preventDefault();
    try {
      await api.post('/access-requests/send/', { unique_id: uniqueId });
      setSuccessMessage('Request sent successfully!');
      setUniqueId('');
      setTimeout(() => {
        setSuccessMessage('');
        handleCloseAccessRequest();
      }, 3000);
    } catch (error) {
      console.error('Error response:', error.response);
      const errorResponse = error.response?.data?.non_field_errors;
      const uuidError = error.response?.data?.unique_id;

      if (errorResponse && errorResponse.includes('There is already a pending access request for this user.')) {
        setErrorMessage('You already have a pending access request.');
      } else if (uuidError && uuidError.includes('Invalid UUID.')) {
        setErrorMessage('The provided UUID is invalid.');
      } else {
        setErrorMessage('An error occurred. Please try again.');
      }
      setTimeout(() => setErrorMessage(''), 3000);
    }
  };

  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">Household Budget</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">Home</Nav.Link>
            </Nav>
            {token ? (
              <>
                <Button variant="outline-light" onClick={handleShowAccessRequest} className="me-2">
                  Request Access
                </Button>
                <Button variant="outline-light" onClick={handleShowLogout}>Logout</Button>
              </>
            ) : (
              <>
                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                <Nav.Link as={Link} to="/register">Register</Nav.Link>
              </>
            )}
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Modal show={showLogoutModal} onHide={handleCloseLogout}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Logout</Modal.Title>
        </Modal.Header>
        <Modal.Body>Are you sure you want to logout?</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseLogout}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleLogout}>
            Logout
          </Button>
        </Modal.Footer>
      </Modal>

      <Modal show={showAccessRequestModal} onHide={handleCloseAccessRequest}>
        <Modal.Header closeButton>
          <Modal.Title>Request Access to Budget</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSendAccessRequest}>
            <Form.Group controlId="uniqueId">
              <Form.Label>Budget Unique ID</Form.Label>
              <Form.Control
                type="text"
                value={uniqueId}
                onChange={(e) => setUniqueId(e.target.value)}
                required
              />
            </Form.Group>
            <Button variant="primary" type="submit" className="mt-3">
              Send Request
            </Button>
          </Form>
          {successMessage && <Alert variant="success" className="mt-3">{successMessage}</Alert>}
          {errorMessage && <Alert variant="danger" className="mt-3">{errorMessage}</Alert>}
        </Modal.Body>
      </Modal>
    </>
  );
}

export default AppNavbar;
