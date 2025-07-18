let cur_index = 1;

function addSpendingField() {
  const container = document.getElementById("spending-container");
  const optionsHTML = document.getElementById("category-options").innerHTML;

  const newGroup = document.createElement("div");
  newGroup.className = "spending-group row mb-3";

  newGroup.innerHTML = `
    <div class="col-md-2">
                <input class="form-control mb-3" type="date" name="transaction_date[${cur_index}]">
            </div>
            <div class="col-md-2">
                <input class="form-control mb-3" type="text" placeholder="Description" name="description[${cur_index}]">
            </div>
            <div class="col-md-2">
                <input class="form-control mb-3" type="number" placeholder="Amount" name="amount[${cur_index}]">
            </div>
            <div class="col-md-3">
                <select name="category[${cur_index}]" class="form-select">
                    <option value="" disabled selected>Select Category</option>
                            ${optionsHTML}
                        </select>
            </div>
            <div class="col-md-3">
                <select class="form-select mb-3 upload-selects" name="payment_method[${cur_index}]" required>
                    <option value="" disabled selected>Select Payment Method</option>
                    <option value="Venmo">Venmo</option>
                    <option value="Cash">Cash</option>
                    <option value="Direct Deposit">Direct Deposit</option>
                    <option value="Delta">Delta</option>
                    <option value="BlueCash">BlueCash</option>
                    <option value="Apple">Apple</option>
                </select>
            </div>
  `;

  container.appendChild(newGroup);
  cur_index++;
  document.getElementById('num_entries').value = String(cur_index);
  console.log(document.getElementById('num_entries').value);
}

function removeLastSpendingField() {
  const container = document.getElementById("spending-container");
  const groups = container.getElementsByClassName("spending-group");
  if (groups.length > 1) {
    container.removeChild(groups[groups.length - 1]);
    cur_index--;
  document.getElementById('num_entries').value = String(cur_index);
  console.log(document.getElementById('num_entries').value);
  }
}