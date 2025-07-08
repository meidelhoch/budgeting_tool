function addFileField() {
  const container = document.getElementById("file-container");

  const newGroup = document.createElement("div");
  newGroup.className = "upload-group row mb-3";

  newGroup.innerHTML = `
    <div class="col-md-5">
        <input class="form-control mb-3 upload-files" type="file" name="files" accept=".csv" required>
    </div>
    <div class="col-md-5">
        <select class="form-select mb-3 upload-selects" name="labels" required>
            <option value="" disabled selected>Select Card</option>
            <option value="Delta">Delta</option>
            <option value="BlueCash">BlueCash</option>
            <option value="Apple">Apple</option>
        </select>
    </div>
  `;

  container.appendChild(newGroup);
}

function removeLastFileField() {
  const container = document.getElementById("file-container");
  const groups = container.getElementsByClassName("upload-group");
  if (groups.length > 1) {
    container.removeChild(groups[groups.length - 1]);
  }
}