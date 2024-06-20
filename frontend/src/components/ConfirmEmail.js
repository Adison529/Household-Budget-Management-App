import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const ConfirmEmail = () => {
    const { uid, token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('loading');
    const [countdown, setCountdown] = useState(3);

    useEffect(() => {
        const confirmEmail = async () => {
            try {
                const response = await axios.get(`https://budgetmanager-web-app-backend.azurewebsites.net/confirm-email/${uid}/${token}/`);
                if (response.status === 200) {
                    setStatus('success');
                } else {
                    setStatus('expired');
                }
            } catch (error) {
                if (error.response && error.response.status === 400) {
                    setStatus('expired');
                } else {
                    setStatus('error');
                }
            }
        };

        confirmEmail();
    }, [uid, token]);

    useEffect(() => {
        if (status === 'success') {
            const interval = setInterval(() => {
                setCountdown((prevCountdown) => {
                    if (prevCountdown <= 1) {
                        clearInterval(interval);
                        navigate('/');
                    }
                    return prevCountdown - 1;
                });
            }, 1000);
        }
    }, [status, navigate]);

    if (status === 'loading') {
        return <div><h1>Awaiting Confirmation</h1><p>Please wait while we confirm your email...</p></div>;
    }

    if (status === 'success') {
        return <div><h1>Email Confirmed</h1><p>Redirecting in {countdown}...</p></div>;
    }

    if (status === 'expired') {
        return <div><h1>Confirmation Link Expired</h1><p>Your confirmation link has expired. Please register again.</p></div>;
    }

    return <div><h1>Error</h1><p>There was an error confirming your email. Please try again later.</p></div>;
};

export default ConfirmEmail;
