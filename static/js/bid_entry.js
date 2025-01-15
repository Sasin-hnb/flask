const valueFields = document.querySelectorAll('.value-field');
const totalValueField = document.getElementById('totalValue');

function calculateTotal() {
  let total = 0;
  valueFields.forEach(field => {
    total += parseFloat(field.value) || 0;
  });
  totalValueField.value = total.toFixed(2);
}

valueFields.forEach(field => {
  field.addEventListener('input', calculateTotal);
});

function bid_sum() {


  showBidConfirmation()

  // Optionally display the result to the user


}

function showBidConfirmation() {
  const totalValue = document.getElementById("totalValue").value;
  const projectName = document.getElementById("projectName").value;
  const address = document.getElementById("address").value;
  const city = document.getElementById("city").value;
  const province = document.getElementById("province").value;
  const projectId = document.getElementById("projectId").value;
  const closingDate = document.getElementById('closingDate').value;


  console.log("Total Sum: ", totalValue);
  document.getElementById('bidConfirmationModal').style.display = 'block';

  document.getElementById('confirmBid').onclick = function () {
    const data = {
      closingDate: closingDate,
      projectName: projectName,
      address: address,
      city: city,
      province: province,
      totalValue: totalValue
      // postalCode: postalCode
    }
    fetch(`/Bid_Entry/${projectId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }).then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
      .then(data => {
        console.log(data);
        closeBidConfirmation();
        alert(data.message)
        window.location.reload()
      })
      .catch(error => {
        console.error('Error updating user:', error);
      });
  }
  document.getElementById('cancelBid').onclick = function () {
    closeBidConfirmation();
  };

  // document.getElementById('modalClose').onclick = function () {
  //   closeBidConfirmation();
  // };
}

// Function to close the modal
function closeBidConfirmation() {
  document.getElementById('bidConfirmationModal').style.display = 'none';
}

