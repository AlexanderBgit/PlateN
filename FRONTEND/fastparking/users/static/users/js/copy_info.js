function copy_user_pwd(e) {
  const button = event.target;
  let parentRow = button.closest("tr");
  if (parentRow) {
    const columns = parentRow.querySelectorAll("td");
    if (columns && columns.length >= 2) {
      const col_user = columns[0];
      const col_pwd = columns[1];
      if (col_user !== undefined) {
        const username = document.getElementById("id_username");
        username.value = col_user.innerText;
      }
      if (col_pwd !== undefined) {
        const password = document.getElementById("id_password");
        password.value = col_pwd.innerText;
      }
    }
  }
}
