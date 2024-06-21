import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Container, Alert, Button, Modal, Form, Badge } from 'react-bootstrap';
import { PencilSquare, Trash } from 'react-bootstrap-icons'; // Import ikony PencilSquare
import api from '../api';

import { Bar, Line, Pie } from 'react-chartjs-2';
import 'chart.js/auto';
import moment from 'moment';
import '../BudgetOperationsGraphs.css';

function BudgetOperations() {
  const { budget_manager_id } = useParams();
  const [operations, setOperations] = useState([]);
  const [error, setError] = useState('');
  const [incomeSum, setIncomeSum] = useState(0);
  const [expenseSum, setExpenseSum] = useState(0);
  const [balance, setBalance] = useState(0);
  const [show, setShow] = useState(false);
  const [editMode, setEditMode] = useState(false); // State to manage edit mode
  const [operationToEdit, setOperationToEdit] = useState(null); // State to store operation to edit
  const [operationTypes, setOperationTypes] = useState([]);
  const [operationCategories, setOperationCategories] = useState([]);
  const [members, setMembers] = useState([]);
  const [currentUserRole, setCurrentUserRole] = useState('');
  const [form, setForm] = useState({
    type: '',
    date: '',
    title: '',
    category: '',
    value: '',
    by: ''
  });

  useEffect(() => {
    const fetchOperations = async () => {
      try {
        const response = await api.get(`/budget-managers/${budget_manager_id}/operations/`);
        const sortedOperations = response.data.sort((a, b) => {
          if (a.date === b.date) {
            return b.id - a.id;
          }
          return new Date(b.date) - new Date(a.date);
        });
        setOperations(sortedOperations);
        const incomeTotal = sortedOperations.filter(op => op.type.name === 'Income').reduce((sum, op) => sum + parseFloat(op.value), 0);
        const expenseTotal = sortedOperations.filter(op => op.type.name === 'Expense').reduce((sum, op) => sum + parseFloat(op.value), 0);
        setIncomeSum(incomeTotal);
        setExpenseSum(expenseTotal);
        setBalance(incomeTotal - expenseTotal);
      } catch (error) {
        setError('There was an error fetching the operations!');
        console.error("There was an error fetching the operations!", error);
      }
    };

    const fetchOperationTypes = async () => {
      try {
        const response = await api.get('/operation-types/');
        setOperationTypes(response.data);
      } catch (error) {
        setError('There was an error fetching the operation types!');
        console.error("There was an error fetching the operation types!", error);
      }
    };

    const fetchOperationCategories = async () => {
      try {
        const response = await api.get('/operation-categories/');
        setOperationCategories(response.data);
      } catch (error) {
        setError('There was an error fetching the operation categories!');
        console.error("There was an error fetching the operation categories!", error);
      }
    };

    const fetchMembers = async () => {
      try {
        const response = await api.get(`/budget-managers/${budget_manager_id}/members/`);
        setMembers(response.data);

        // Find current user in members list and set role
        const username = localStorage.getItem('username');
        const currentUser = response.data.find(member => member.user.username === username);
        if (currentUser) {
          setCurrentUserRole(currentUser.role);
        } else {
          setCurrentUserRole('');
        }
      } catch (error) {
        setError('There was an error fetching the members!');
        console.error("There was an error fetching the members!", error);
      }
    };

    fetchOperations();
    fetchOperationTypes();
    fetchOperationCategories();
    fetchMembers();
  }, [budget_manager_id]);

  const processExpenseIncomeData = (operations) => {
    const dataByMonth = {};

    operations.forEach(op => {
      const month = moment(op.date).format('YYYY-MM');

      if (!dataByMonth[month]) {
        dataByMonth[month] = { income: 0, expense: 0 };
      }

      if (op.type.name === 'Income') {
        dataByMonth[month].income += parseFloat(op.value);
      } else {
        dataByMonth[month].expense += parseFloat(op.value);
      }
    });

    const labels = Object.keys(dataByMonth).sort();
    const incomeData = labels.map(label => dataByMonth[label].income);
    const expenseData = labels.map(label => dataByMonth[label].expense);

    return {
      labels,
      datasets: [
        {
          label: 'Monthly Income',
          data: incomeData,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: 'Monthly Expenses',
          data: expenseData,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
        },
      ],
    };
  };

  const processBalanceData = (operations) => {
    const balanceByMonth = {};
    const monthlyOperations = {};
  
    // Group operations by month
    operations.forEach(op => {
      const month = moment(op.date).format('YYYY-MM');
  
      if (!monthlyOperations[month]) {
        monthlyOperations[month] = [];
      }
  
      monthlyOperations[month].push(op);
    });
  
    // Calculate balance for each month
    Object.keys(monthlyOperations).forEach(month => {
      let cumulativeIncome = 0;
      let cumulativeExpenses = 0;
  
      monthlyOperations[month].forEach(op => {
        if (op.type.name === 'Income') {
          cumulativeIncome += parseFloat(op.value);
        } else {
          cumulativeExpenses += parseFloat(op.value);
        }
      });
  
      balanceByMonth[month] = cumulativeIncome - cumulativeExpenses;
    });
  
    const labels = Object.keys(balanceByMonth).sort();
    const data = labels.map(label => balanceByMonth[label]);
  
    return {
      labels,
      datasets: [{
        label: 'Monthly Balance',
        data,
        fill: false,
        borderColor: 'rgba(75, 192, 192, 1)',
        tension: 0.1,
        yAxisID: 'balance-y-axis',
      }],
    };
  };  

  const processCurrentMonthCategoryData = (operations) => {
    const currentMonth = moment().format('YYYY-MM');
    const expensesByCategory = {};

    operations.filter(op => op.type.name === 'Expense' && moment(op.date).format('YYYY-MM') === currentMonth).forEach(op => {
      if (!expensesByCategory[op.category.name]) {
        expensesByCategory[op.category.name] = 0;
      }

      expensesByCategory[op.category.name] += parseFloat(op.value);
    });

    const labels = Object.keys(expensesByCategory);
    const data = labels.map(label => expensesByCategory[label]);

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(255, 206, 86, 0.2)',
          'rgba(75, 192, 192, 0.2)',
          'rgba(153, 102, 255, 0.2)',
          'rgba(255, 159, 64, 0.2)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1,
      }],
    };
  };

  const handleShow = () => setShow(true);
  const handleClose = () => {
    setShow(false);
    setEditMode(false); // Reset edit mode when modal is closed
    setOperationToEdit(null); // Clear operation to edit when modal is closed
    resetForm(); // Reset form fields when modal is closed
  };

  const handleEditOperation = (operation) => {
    setOperationToEdit(operation);
    setEditMode(true);
    setShow(true);
    setForm({
      type: operation.type.id.toString(),
      date: operation.date,
      title: operation.title,
      category: operation.category.id.toString(),
      value: operation.value.toString(),
      by: operation.by ? operation.by.id.toString() : ''
    });
  };

  const handleDeleteOperation = async (operation) => {
    if (window.confirm(`Are you sure you want to delete the operation "${operation.title}"?`)) {
      try {
        await api.delete(`/budget-managers/${budget_manager_id}/operations/${operation.id}/delete/`);
        window.location.reload();
      } catch (error) {
        const errorMessage = error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message;
        setError(`There was an error deleting the operation: ${errorMessage}`);
        console.error("There was an error deleting the operation!", error.response?.data || error);
      }
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prevForm => ({
      ...prevForm,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const operationData = {
      type: parseInt(form.type), // Ensure type is sent as an integer ID
      category: parseInt(form.category), // Ensure category is sent as an integer ID
      date: form.date,
      title: form.title,
      value: parseFloat(form.value), // Ensure value is a number
      budget_manager: budget_manager_id
    };

    if (form.by) {
      operationData.by = parseInt(form.by);
    } else {
      operationData.by = null; // Set by to null if no user is selected
    }

    try {
      if (editMode && operationToEdit) {
        await api.put(`/budget-managers/${budget_manager_id}/operations/${operationToEdit.id}/edit/`, operationData);
      } else {
        await api.post(`/budget-managers/${budget_manager_id}/operations/add/`, operationData);
      }
      setShow(false);
      window.location.reload(); // Reload the page after adding/editing the operation
    } catch (error) {
      const errorMessage = error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message;
      setError(`There was an error ${editMode ? 'editing' : 'creating'} the operation: ${errorMessage}`);
      console.error(`There was an error ${editMode ? 'editing' : 'creating'} the operation!`, error.response?.data || error);
    }
  };

  const resetForm = () => {
    setForm({
      type: '',
      date: '',
      title: '',
      category: '',
      value: '',
      by: ''
    });
  };

  return (
    <Container className="mt-4">
      <h2>Budget Operations</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <div className="d-flex justify-content-between mb-3">
        <div>
          <h4 className="mb-0">Income: <Badge bg="success">${incomeSum.toFixed(2)}</Badge></h4>
        </div>
        <div>
          <h4 className="mb-0">Expenses: <Badge bg="danger">${expenseSum.toFixed(2)}</Badge></h4>
        </div>
        <div>
          <h4 className="mb-0">Balance: <Badge bg={balance >= 0 ? 'success' : 'danger'}>${balance.toFixed(2)}</Badge></h4>
        </div>
      </div>
      {(currentUserRole === 'admin' || currentUserRole === 'edit') && (
        <Button variant="primary" onClick={handleShow}>
          Add Operation
        </Button>
      )}
      <Table striped bordered hover className="mt-3">
        <thead>
          <tr>
            <th>Type</th>
            <th>Date</th>
            <th>Title</th>
            <th>Category</th>
            <th>Value</th>
            <th>User</th>
            {(currentUserRole === 'admin' || currentUserRole === 'edit') && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {operations.map(operation => (
            <tr key={operation.id}>
              <td style={{ color: operation.type.name === 'Income' ? 'green' : 'red' }}>
                {operation.type.name}
              </td>
              <td>{operation.date}</td>
              <td>{operation.title}</td>
              <td>{operation.category.name}</td>
              <td style={{ color: operation.type.name === 'Income' ? 'green' : 'red' }}>
                ${parseFloat(operation.value).toFixed(2)}
              </td>
              <td>{operation.by ? operation.by.username : 'N/A'}</td>
              {(currentUserRole === 'admin' || currentUserRole === 'edit') && (
                <td>
                  <Button variant="info" onClick={() => handleEditOperation(operation)}>
                    <PencilSquare /> Edit
                  </Button>
                  &nbsp;
                  <Button variant="danger" onClick={() => handleDeleteOperation(operation)}>
                    <Trash /> Delete
                  </Button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </Table>
  
      {operations.length > 0 && (
        <div className="mt-4 graph-container">
          <div className="row justify-content-center">
            <div className="col-md-4">
              <h5 className="text-center">Income & expenses for each month</h5>
              <Bar data={processExpenseIncomeData(operations)} options={{ responsive: true }} />
            </div>
            <div className="col-md-4">
              <h5 className="text-center">Monthly balance</h5>
              <Line data={processBalanceData(operations)} options={{ responsive: true }} />
            </div>
            <div className="col-md-4">
              <h5 className="text-center">Your expenses this month</h5>
              <Pie 
                data={processCurrentMonthCategoryData(operations)} 
                options={{
                  plugins: {
                    tooltip: {
                      callbacks: {
                        label: function(tooltipItem) {
                          return `$${tooltipItem.raw.toFixed(2)}`;
                        }
                      }
                    }
                  }
                }} 
              />
            </div>
          </div>
        </div>
      )}
  
      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>{editMode ? 'Edit Operation' : 'Add Operation'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formType">
              <Form.Label>Type</Form.Label>
              <Form.Control
                as="select"
                name="type"
                value={form.type}
                onChange={handleChange}
                required
              >
                <option value="">Select type</option>
                {operationTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.name}</option>
                ))}
              </Form.Control>
            </Form.Group>
            <Form.Group controlId="formDate">
              <Form.Label>Date</Form.Label>
              <Form.Control
                type="date"
                name="date"
                value={form.date}
                onChange={handleChange}
                required
              />
            </Form.Group>
            <Form.Group controlId="formTitle">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                name="title"
                placeholder="Enter title"
                value={form.title}
                onChange={handleChange}
                required
              />
            </Form.Group>
            <Form.Group controlId="formCategory">
              <Form.Label>Category</Form.Label>
              <Form.Control
                as="select"
                name="category"
                value={form.category}
                onChange={handleChange}
                required
              >
                <option value="">Select category</option>
                {operationCategories.map(category => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </Form.Control>
            </Form.Group>
            <Form.Group controlId="formValue">
              <Form.Label>Value</Form.Label>
              <Form.Control
                type="number"
                name="value"
                placeholder="Enter value"
                value={form.value}
                onChange={handleChange}
                required
              />
            </Form.Group>
            <Form.Group controlId="formBy">
              <Form.Label>User</Form.Label>
              <Form.Control
                as="select"
                name="by"
                value={form.by}
                onChange={handleChange}
              >
                <option value="">Select user</option>
                {members.map(member => (
                  <option key={member.id} value={member.user.id}>{member.user.username}</option>
                ))}
              </Form.Control>
            </Form.Group>
            <Button variant="primary" type="submit" className="mt-3">
              {editMode ? 'Save Changes' : 'Add Operation'}
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );  
}

export default BudgetOperations;
