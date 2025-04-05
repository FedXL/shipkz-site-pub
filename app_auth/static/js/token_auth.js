

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function checkTokenUnregisterUser() {
    return new Promise((resolve, reject) => {
        const token = getCookie('ShipKZAuthorization');
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ token: token })
            })
            .then(response => {
                if (!response.ok) {
                    reject(new Error('Network response was not ok'));
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                if (data.token) {
                    setCookie('ShipKZAuthorization', data.token, 14);
                }
                resolve();  // Успешно завершили, вызываем resolve
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                reject(error);  // В случае ошибки вызываем reject
            });
        } else {
            console.error('CSRF token not found in cookies');
            reject(new Error('CSRF token not found in cookies'));
        }
    });
}
