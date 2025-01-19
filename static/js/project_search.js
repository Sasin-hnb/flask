let project_id;


document.getElementById('searchForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Clear previous results and errors
    document.getElementById('projectList').innerHTML = '';
    document.getElementById('errorContainer').innerText = '';

    // Get input values
    const projectName = document.getElementById('projectName').value;
    const address = document.getElementById('address').value;
    const city = document.getElementById('city').value;
    const province = document.getElementById('province').value;
    const postalCode = document.getElementById('postalCode').value;

    // Build query string
    const query = new URLSearchParams({
        projectName,
        address,
        city,
        province,
        postalCode
    }).toString();

    // Send the GET request to the API
    fetch(`/project_search/search?${query}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Check if we have results
            if (data.length === 0) {
                document.getElementById('errorContainer').innerText = 'No projects found.';
                document.getElementById('ConfirmationModal').style.display = 'block';

            } else {
                // Display the results
                data.forEach(project => {
                    const projectDiv = document.createElement('div');
                    projectDiv.className = 'project';
                    projectDiv.innerHTML = `
                        <div class="project-item" data-project-name="${project.projectName}" data-project-id="${project.id}">
                            <h3>${project.projectName}</h3>
                            <p>${project.address}, ${project.city}, ${project.province}, ${project.postalCode}</p>
                        </div>
                    `;
                    document.getElementById('projectList').appendChild(projectDiv);
                });

                // Add click event to each project item
                const projectItems = document.querySelectorAll('.project-item');
                projectItems.forEach(item => {
                    item.addEventListener('click', function () {
                        const projectId = this.getAttribute('data-project-id');
                        project_id = projectId;
                        showBidConfirmation(projectId);
                    });
                });
            }
        })
        .catch(error => {
            document.getElementById('errorContainer').innerText = 'An error occurred while fetching the projects.';
            console.error('There was a problem with the fetch operation:', error);
        });
});


// Function to show the bid confirmation modal
function showBidConfirmation(projectId) {

    fetch(`/project_search/bid/${projectId}`)
    .then(response => {
        return response.json();
      })
    .then(data => {
        console.log("mmmmmmmmmmm",data)
        // alert(data.message)
        if (data.state == 1) {
            document.getElementById("errorMessage").textContent = "You can edit your bid after 24 hours!"
            document.getElementById('errorConfirmationModal').style.display = 'block';
            // window.location.reload();
        } if (data.state == 2) {
            document.getElementById("errorMessage").textContent = "No revisions allowed; project is closed!"
            document.getElementById('errorConfirmationModal').style.display = 'block';
        } if (data.state == 3) {
            document.getElementById("editMessage").textContent = "Do you wish to edit your bid for this project?"
            // document.getElementById('editConfirmationModal').style.display = 'block';
            document.getElementById('editbid').style.display = 'block';
            
        } 
        else {
            
            document.getElementById('bidConfirmationModal').style.display = 'block';

            document.getElementById('confirmBid').onclick = function () {
                // Handle Yes click (e.g. submit a bid)
                console.log(`Submitting bid for project ID: ${projectId}`);
                window.location.href = `/Bid_Entry/${projectId}`
                closeBidConfirmation();
            };
        }
    })
    .catch(error => { 
        console.error('Error: ', error);
    })

    document.getElementById('cancelBid').onclick = function () {
        closeBidConfirmation();
    };


}

document.getElementById('confirmtogoproject').onclick = function () {
    window.location.href = '/add_project';
    closeBidConfirmation();

};

// Function to close the modal
function closeBidConfirmation() {
    document.getElementById('bidConfirmationModal').style.display = 'none';
    document.getElementById('editConfirmationModal').style.display = 'none';
    document.getElementById('errorConfirmationModal').style.display = 'none';
    document.getElementById('editbid').style.display = 'none';
}

function cancelConfirm() {
    document.getElementById('ConfirmationModal').style.display = 'none';
}

function updateClosingDate(projectId) {
    const date = document.getElementById('editClosingDate').value;
    const data = {date}
    fetch(`/editbid/${project_id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
    .then(data => {
        console.log(data.message)
        alert(data.message)
        closeBidConfirmation()
    })
}
