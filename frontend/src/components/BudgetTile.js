import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Form, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeSlash, Clipboard, PencilSquare, BellFill, CheckCircle, XCircle, PeopleFill, Trash } from 'react-bootstrap-icons';
import api from '../api';
import '../BudgetTile.css'; // Import dodatkowego pliku CSS

function BudgetTile({ budget, currentUser }) {
  const navigate = useNavigate();
  const [showUniqueId, setShowUniqueId] = useState(false);
  const [showCopyModal, setShowCopyModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showRequestsModal, setShowRequestsModal] = useState(false);
  const [showMembersModal, setShowMembersModal] = useState(false);
  const [newBudgetName, setNewBudgetName] = useState(budget.name);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hasPendingRequests, setHasPendingRequests] = useState(false);
  const [accessRequests, setAccessRequests] = useState([]);
  const [members, setMembers] = useState([]);
  const [userRole, setUserRole] = useState('');
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false);
  const [showBudgetDeleteConfirmModal, setShowBudgetDeleteConfirmModal] = useState(false);
  const [memberToDelete, setMemberToDelete] = useState(null);

  useEffect(() => {
    const username = localStorage.getItem('username');
    if (username) {
      const userMember = members.find(member => member.user.username === username);
      if (userMember) {
        setUserRole(userMember.role);
      }
    }
  }, [members]);

  useEffect(() => {
    if (currentUser && currentUser.username === budget.admin.username) {
      api.get(`/budget-managers/${budget.id}/access-requests/`)
        .then(response => {
          const pendingRequests = response.data.filter(request => request.status === 'pending');
          if (pendingRequests.length > 0) {
            setHasPendingRequests(true);
            setAccessRequests(pendingRequests);
          }
        })
        .catch(error => {
          console.error("There was an error fetching the access requests!", error);
        });
    }
  }, [budget.id, currentUser, budget.admin.username]);

  const handleClick = () => {
    navigate(`/budget-managers/${budget.id}/operations`);
  };

  const handleToggleUniqueId = (e) => {
    e.stopPropagation(); // Prevent card click event
    setShowUniqueId(!showUniqueId);
  };

  const handleCopyUniqueId = (e) => {
    e.stopPropagation(); // Prevent card click event
    navigator.clipboard.writeText(budget.unique_id);
    setShowCopyModal(true);
    setTimeout(() => setShowCopyModal(false), 1500);
  };

  const handleEditModalShow = (e) => {
    e.stopPropagation(); // Prevent card click event
    setShowEditModal(true);
  };

  const handleEditModalClose = () => setShowEditModal(false);

  const handleRequestsModalShow = (e) => {
    e.stopPropagation(); // Prevent card click event
    setShowRequestsModal(true);
  };

  const handleRequestsModalClose = () => setShowRequestsModal(false);

  const handleMembersModalShow = (e) => {
    e.stopPropagation(); // Prevent card click event
    api.get(`/budget-managers/${budget.id}/members/`)
      .then(response => {
        setMembers(response.data);
        setShowMembersModal(true);
      })
      .catch(error => {
        console.error("There was an error fetching the budget members!", error);
      });
  };

  const handleMembersModalClose = () => setShowMembersModal(false);

  const handleEditBudgetName = (e) => {
    e.preventDefault();
    if (newBudgetName && newBudgetName !== budget.name) {
      api.patch(`/budget-managers/${budget.id}/edit/`, { name: newBudgetName })
        .then(response => {
          setSuccess('Budget name updated successfully!');
          setShowEditModal(false);
          // Refresh the page or trigger a state update to reflect the change
          window.location.reload();
        })
        .catch(error => {
          setError('There was an error updating the budget name!');
          console.error("There was an error updating the budget name!", error);
        });
    } else {
      setError('New budget name must be different from the current name and cannot be empty.');
    }
  };

  const handleAccessRequestAction = (requestId, action) => {
    api.patch(`/budget-managers/${budget.id}/access-requests/${requestId}/edit/`, { status: action })
      .then(response => {
        const updatedRequests = accessRequests.filter(request => request.id !== requestId);
        setAccessRequests(updatedRequests);
        if (updatedRequests.length === 0) {
          setHasPendingRequests(false);
          setTimeout(() => setShowRequestsModal(false), 1500);
        }
      })
      .catch(error => {
        console.error(`There was an error ${action === 'accepted' ? 'accepting' : 'denying'} the access request!`, error);
      });
  };

  const handleRoleChange = (memberId, newRole) => {
    api.patch(`/budget-managers/${budget.id}/user-access/${memberId}/edit/`, { role: newRole })
      .then(response => {
        setMembers(members.map(member => member.id === memberId ? { ...member, role: newRole } : member));
      })
      .catch(error => {
        console.error("There was an error updating the member's role!", error);
      });
  };

  const handleDeleteMember = (memberId) => {
    api.delete(`/budget-managers/${budget.id}/user-access/${memberId}/delete/`)
      .then(response => {
        setMembers(members.filter(member => member.id !== memberId));
        setShowDeleteConfirmModal(false);
      })
      .catch(error => {
        console.error("There was an error deleting the member!", error);
      });
  };

  const handleShowDeleteConfirm = (memberId) => {
    setMemberToDelete(memberId);
    setShowDeleteConfirmModal(true);
  };

  const handleCloseDeleteConfirm = () => {
    setShowDeleteConfirmModal(false);
    setMemberToDelete(null);
  };

  const handleBudgetDeleteConfirmShow = (e) => {
    e.stopPropagation(); // Prevent card click event
    setShowBudgetDeleteConfirmModal(true);
  };

  const handleBudgetDeleteConfirmClose = () => {
    setShowBudgetDeleteConfirmModal(false);
  };

  const handleDeleteBudget = () => {
    api.delete(`/budget-managers/${budget.id}/delete/`)
      .then(response => {
        setShowBudgetDeleteConfirmModal(false);
        window.location.reload(); // Refresh the page or navigate to another page
      })
      .catch(error => {
        console.error("There was an error deleting the budget!", error);
      });
  };

  return (
    <>
      <Card
        className="budget-card"
        onClick={handleClick}
      >
        <Card.Body className="budget-card-body">
          <Card.Title className="budget-card-title">
            {budget.name}
            {currentUser && currentUser.username === budget.admin.username && (
              <Button variant="link" onClick={handleEditModalShow} className="budget-card-icon">
                <PencilSquare />
              </Button>
            )}
          </Card.Title>
          {currentUser && currentUser.username === budget.admin.username && (
            <Card.Text className="budget-card-text">
              Budget ID: {showUniqueId ? budget.unique_id : '****'}
              <Button variant="link" onClick={handleToggleUniqueId} className="budget-card-icon">
                {showUniqueId ? <EyeSlash /> : <Eye />}
              </Button>
              {showUniqueId && (
                <Button variant="link" onClick={handleCopyUniqueId} className="budget-card-icon">
                  <Clipboard />
                </Button>
              )}
            </Card.Text>
          )}
          {currentUser && currentUser.username === budget.admin.username && (
            hasPendingRequests ? (
              <BellFill
                onClick={handleRequestsModalShow}
                className="budget-card-notification"
              />
            ) : (
              <Trash
                onClick={handleBudgetDeleteConfirmShow}
                className="budget-card-trash"
              />
            )
          )}
          <PeopleFill
            onClick={handleMembersModalShow}
            className="budget-card-people"
          />
        </Card.Body>
      </Card>

      <Modal show={showCopyModal} onHide={() => setShowCopyModal(false)} centered>
        <Modal.Body>
          <p>Unique ID copied to clipboard!</p>
        </Modal.Body>
      </Modal>

      <Modal show={showEditModal} onHide={handleEditModalClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Edit Budget Name</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          <Form onSubmit={handleEditBudgetName}>
            <Form.Group controlId="formNewBudgetName">
              <Form.Label>New Budget Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter new budget name"
                value={newBudgetName}
                onChange={(e) => setNewBudgetName(e.target.value)}
                required
              />
            </Form.Group>
            <Button variant="primary" type="submit" className="mt-3">
              Save Changes
            </Button>
          </Form>
        </Modal.Body>
      </Modal>

      <Modal show={showRequestsModal} onHide={handleRequestsModalClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Access Requests</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {accessRequests.length > 0 ? (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {accessRequests.map(request => (
                <li key={request.id} className="access-request-item">
                  {request.user.username}
                  <div>
                    <Button
                      variant="success"
                      onClick={() => handleAccessRequestAction(request.id, 'accepted')}
                      className="budget-card-icon"
                    >
                      <CheckCircle />
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => handleAccessRequestAction(request.id, 'denied')}
                      className="budget-card-icon"
                    >
                      <XCircle />
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>No pending access requests.</p>
          )}
        </Modal.Body>
      </Modal>

      <Modal show={showMembersModal} onHide={handleMembersModalClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Budget Members</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {members.length > 0 ? (
            <ul className="members-list">
              {members.map(member => (
                <li key={member.id} className="member-item">
                  {userRole === 'admin' && member.user.username !== currentUser.username && (
                    <Trash
                      onClick={() => handleShowDeleteConfirm(member.id)}
                      className="budget-card-trash"
                    />
                  )}
                  <span className="member-name">
                    {member.user.username}
                    {userRole === 'admin' && member.user.username === currentUser.username && ` - ${member.role}`}
                  </span>
                  {userRole === 'admin' && member.user.username !== currentUser.username && (
                    <Form.Control
                      as="select"
                      value={member.role}
                      onChange={(e) => handleRoleChange(member.id, e.target.value)}
                      className="role-select"
                    >
                      <option value="read_only">Read Only</option>
                      <option value="edit">Edit</option>
                    </Form.Control>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p>No members in this budget.</p>
          )}
        </Modal.Body>
      </Modal>

      <Modal show={showDeleteConfirmModal} onHide={handleCloseDeleteConfirm} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to remove this member from the budget?</p>
          <Button variant="danger" onClick={() => handleDeleteMember(memberToDelete)}>Delete</Button>
          <Button variant="secondary" onClick={handleCloseDeleteConfirm} style={{ marginLeft: '10px' }}>Cancel</Button>
        </Modal.Body>
      </Modal>

      <Modal show={showBudgetDeleteConfirmModal} onHide={handleBudgetDeleteConfirmClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete this budget?</p>
          <Button variant="danger" onClick={handleDeleteBudget}>Delete</Button>
          <Button variant="secondary" onClick={handleBudgetDeleteConfirmClose} style={{ marginLeft: '10px' }}>Cancel</Button>
        </Modal.Body>
      </Modal>
    </>
  );
}

export default BudgetTile;
