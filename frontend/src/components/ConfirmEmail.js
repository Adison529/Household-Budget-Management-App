// src/components/ConfirmEmail.js
import React, { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const ConfirmEmail = () => {
    const { uid, token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('awaiting_confirmation');
    const [message, setMessage] = useState('');

    const confirmEmail = useCallback(async () => {
        try {
            const response = await axios.post(`https://budgetmanager-web-app-backend.azurewebsites.net/api/confirm-email/${uid}/${token}/`);
            if (response.data.status === 'success') {
                setStatus('success');
                setTimeout(() => {
                    navigate('/');
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

    if (status === 'awaiting_confirmation') {
        return (
            <div>
                <h1>Email Confirmation</h1>
                <p>Click the button below to confirm your email:</p>
                <button onClick={confirmEmail}>Confirm Email</button>
            </div>
        );
    }

    if (status === 'success') {
        return (
            <div>
                <h1>Email Confirmed</h1>
                <p>Redirecting to the homepage in 3 seconds...</p>
            </div>
        );
    }

    if (status === 'error') {
        return (
            <div>
                <h1>Error</h1>
                <p>{message}</p>
            </div>
        );
    }

    return <div><h1>Loading...</h1></div>;
};

export default ConfirmEmail;
