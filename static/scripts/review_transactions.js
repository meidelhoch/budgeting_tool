document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.reimbursed-checkbox').forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const row = this.dataset.row;

            // Find the hidden amount input for this row
            const amountInput = document.querySelector(`.amount[data-row="${row}"]`);
            const amount = parseFloat(amountInput?.value || "0");

            // Find the reimbursement amount input
            const reimbursementInput = document.querySelector(`.reimbursement-amount[data-row="${row}"]`);

            if (this.checked) {
                reimbursementInput.value = amount.toFixed(2);  // Fill with full amount
            } else {
                reimbursementInput.value = '';  // Optional: clear when unchecked
            }
        });
    });
    document.querySelectorAll('.reimbursement-amount').forEach(function (input) {
        input.addEventListener('input', function () {
            const row = this.dataset.row;
            const checkbox = document.querySelector(`.reimbursed-checkbox[data-row="${row}"]`);

            // If user enters a non-empty, non-zero value, check the box
            if (this.value.trim() !== '' && parseFloat(this.value) !== 0) {
                checkbox.checked = true;
            } else {
                checkbox.checked = false;
            }
        });
    });
    const cancelButton = document.getElementById('cancel-button');
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            // This will be replaced by Flask when the template is rendered
            window.location.href = "/upload-statements";
        });
    }
});



