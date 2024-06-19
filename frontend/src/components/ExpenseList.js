import React, { useEffect, useState } from 'react';
import { Table, Container, Alert } from 'react-bootstrap';
import api from '../api';

function ExpenseList() {
  const [expenses, setExpenses] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/operations/')
      .then(response => {
        setExpenses(response.data);
      })
      .catch(error => {
        setError('There was an error fetching the expenses!');
        console.error("There was an error fetching the expenses!", error);
      });
  }, []);

  return (
    <Container className="mt-4">
      <h2>Expenses</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Amount</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map(expense => (
            <tr key={expense.id}>
              <td>{expense.name}</td>
              <td>${expense.amount}</td>
              <td>{expense.date}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
}

export default ExpenseList;
