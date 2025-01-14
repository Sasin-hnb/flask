let userIdToDelete = null; // Global variable to hold the user ID


function showLogoutPopup() {
  document.getElementById('logoutPopup').style.display = 'flex';
}

function closeLogoutPopup() {
  document.getElementById('logoutPopup').style.display = 'none';
}

function showConfirmModal() {
  document.getElementById('confirmModal').style.display = 'block';
}

function confirmLogout() {
  window.location.href = '/';  // Redirect to the homepage
}

// Function to close the modal
function closeModal() {
  document.getElementById('editUserModal').style.display = 'none';
  document.getElementById('confirmModal').style.display = 'none';
  userIdToDelete = null; // Reset user ID when modal is closed
}

// --------------Start Edit User --------------- //


function editUser(user_id) {
  fetch(`/user_management/${user_id}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data); // Handle the user data here
      // You can populate your modal or form with this data
      document.getElementById('userId').value = data.id
      document.getElementById('username').value = data.username;
      document.getElementById('role').value = data.role;
      document.getElementById('editUserModal').style.display = 'block';
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
}

function updateUser() {
  const userId = document.getElementById('userId').value;
  const username = document.getElementById('username').value;
  const role = document.getElementById('role').value;
  // const email = document.getElementById('email').value; // Uncomment if email is needed

  const data = {
    username: username,
    // email: email, // Uncomment if email is needed
    role: role
  };

  fetch(`/user_management/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      // Handle successful response (e.g., close modal)
      closeModal();
      window.location.reload()
    })
    .catch(error => {
      console.error('Error updating user:', error);
    });
}


// --------------End Edit User --------------- //

// -------------- Start delete user ------------- //

function removeUser(user_id) {
    userIdToDelete = user_id; // Set the user ID to delete
    showConfirmModal(); // Show the confirmation modal
}

function showConfirmModal() {
    document.getElementById('confirmModal').style.display = 'block';
}

function confirmAction() {
    if (userIdToDelete) {
        fetch(`/user_management/${userIdToDelete}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            console.log(data);
            closeModal(); // Close modal after the action
            window.location.reload();
        }).catch(error => {
            console.error('Error deleting user:', error);
        });
    }
}

// ------------- End delete User -------------- //
