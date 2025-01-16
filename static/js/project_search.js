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
    document.getElementById('bidConfirmationModal').style.display = 'block';

    document.getElementById('confirmBid').onclick = function () {
        // Handle Yes click (e.g. submit a bid)
        console.log(`Submitting bid for project ID: ${projectId}`);
        window.location.href = `/Bid_Entry/${projectId}`
        closeBidConfirmation();
    };

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
}

function cancelConfirm() {
    document.getElementById('ConfirmationModal').style.display = 'none';
}