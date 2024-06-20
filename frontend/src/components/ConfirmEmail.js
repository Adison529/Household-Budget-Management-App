import React, { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Button, Alert } from 'react-bootstrap';
import axios from 'axios';

const ConfirmEmail = () => {
    const { uid, token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('awaiting_confirmation');
    const [message, setMessage] = useState('');

    const confirmEmail = useCallback(async () => {
        try {
            const baseURL = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'https://budgetmanager-web-app-backend.azurewebsites.net';
            const response = await axios.post(`${baseURL}/api/confirm-email/${uid}/${token}/`);
            if (response.data.status === 'success') {
                setStatus('success');
                setTimeout(() => {
                    navigate('/login');
                }, 3000);
            } else {
                setStatus('error');
                setMessage(response.data.message);
            }
        } catch (error) {
            setStatus('error');
            setMessage('There was an error confirming your email. Please try again later.');
        }
    }, [uid, token, navigate]);

    return (
        <Container className="mt-5">
            <Row className="justify-content-md-center">
                <Col md="6">
                    {status === 'awaiting_confirmation' && (
                        <>
                            <h1>Email Confirmation</h1>
                            <p>Click the button below to confirm your email:</p>
                            <Button variant="primary" onClick={confirmEmail}>Confirm Email</Button>
                        </>
                    )}
                    {status === 'success' && (
                        <Alert variant="success">
                            <h4>Email Confirmed</h4>
                            <p>Redirecting to the login page in 3 seconds...</p>
                        </Alert>
                    )}
                    {status === 'error' && (
                        <Alert variant="danger">
                            <h4>Error</h4>
                            <p>{message}</p>
                        </Alert>
                    )}
                    {status === 'loading' && (
                        <div>
                            <h1>Loading...</h1>
                        </div>
                    )}
                </Col>
            </Row>
        </Container>
    );
};

export default ConfirmEmail;
