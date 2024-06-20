import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const ConfirmEmail = () => {
    const { uid, token } = useParams();
    const [status, setStatus] = useState('loading');
    const [message, setMessage] = useState('');

    const confirmEmail = async () => {
        try {
            const response = await axios.post(`https://budgetmanager-web-app-backend.azurewebsites.net/api/confirm-email/${uid}/${token}/`);
            if (response.data.status === 'success') {
                setStatus('success');
            } else {
                setStatus('error');
                setMessage(response.data.message);
            }
        } catch (error) {
            setStatus('error');
            setMessage('There was an error confirming your email. Please try again later.');
        }
    };

    useEffect(() => {
        setStatus('awaiting_confirmation');
    }, []);

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
