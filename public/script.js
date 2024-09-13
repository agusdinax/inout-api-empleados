document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const usernameSpan = document.getElementById('username');
    const dataTableBody = document.querySelector('#dataTable tbody');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    window.location.href = 'dashboard.html';
                } else {
                    const errorData = await response.json();
                    errorMessage.textContent = errorData.error;
                }
            } catch (error) {
                console.error('Error:', error);
                errorMessage.textContent = 'Error en la solicitud';
            }
        });
    }

    if (usernameSpan) {
        usernameSpan.textContent = 'Usuario'; // Aquí puedes obtener el nombre de usuario desde la sesión en el backend
    }

    if (dataTableBody) {
        fetch('/dashboard')
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.id}</td>
                        <td>${item.name}</td>
                        <td>${item.price}</td>
                    `;
                    dataTableBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error:', error));
    }
});
