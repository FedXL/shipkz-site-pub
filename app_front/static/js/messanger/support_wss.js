

console.log('im life');
console.log(wsUrl);

const isAuth = AuthUserIs;

let chatSocket;

if (isAuth) {
    console.log('User is authenticated');
    chatSocket = new WebSocket(wsUrl);
} else {
    const token = checkToken();
    if (token) {
        console.log('User is not authenticated but has a token');
        chatSocket = new WebSocket(wsUrl);
    } else {
        console.log('User is not authenticated and no token found');
    }
}

let UnreadMessagesCounter;

if (chatSocket) {
    chatSocket.onopen = function (e) {
        console.log("Connected to WebSocket.");
    };
    chatSocket.onmessage = function (e) {
    console.log('we got a message');
        const data = JSON.parse(e.data);
        console.log(data);
        if (data.message_type === 'update_counter') {
            const miniMessangerButton = document.getElementById('messengerMiniButton');
            if (miniMessangerButton) {
                UnreadMessagesCounter = miniMessangerButton.querySelector('.miniMessangerUnreadCounter');
            }

            const LkUnreadMessageButton = document.getElementById('lk-message-button');

            if (data.count > 0) {
                if (miniMessangerButton) {
                    miniMessangerButton.classList.add('createSignal');
                }
                if (UnreadMessagesCounter) {
                    UnreadMessagesCounter.classList.add('createSignal');
                    UnreadMessagesCounter.innerText = data.count;
                }
                if  (LkUnreadMessageButton) {
                    LkUnreadMessageButton.classList.add('createSignalLK');
                    let CounterCyrcle = LkUnreadMessageButton.querySelector('.unread-messages-counter');
                    CounterCyrcle.innerText = data.count;

                    CounterCyrcle.style.display = 'flex';
                }

            } else {
            try {
                    miniMessangerButton.classList.remove('createSignal');
                    LkUnreadMessageButton.classList.remove('createSignalLK');
                  }
            catch (e) {
                console.log('No unread messages');
                }
            }
            }
    }

};

    chatSocket.onclose = function (e) {
        console.log("WebSocket closed.");
    };


function checkToken() {
    if (document.cookie.includes('ShipKZAuthorization')) {
        const cookies = document.cookie.split('; ').reduce((acc, cookie) => {
        const [key, value] = cookie.split('=');
        acc[key] = value;
        return acc;
        }, {});

        return cookies['ShipKZAuthorization'] || null;
    }
    return null;
}
