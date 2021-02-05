
/*const roomName = JSON.parse(document.getElementById('room-name').textContent);
const username = JSON.parse(document.getElementById('username').textContent);
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);
var newChatMembers = [];
var msgHtml = '';
var msgHtmlEnd = '</div>'
var timeHtml = '<div class="message-time">'
var timeHtmlEng = '</div>'
var containerEnd = '</div>\
    </div>';*/

class ChatSocket {
    constructor(roomName, username) {
        this.socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + roomName
            + '/'
        );
        this.username = username;
        this.socket.onmessage = function(msg){
            const message = JSON.parse(msg.data);
            console.log(message.send_type)
            if (message.send_type == 'chat') {
                // load message
                loadMessage(message, username)
            } else if (message.send_type == 'search') {
                // display people
                findPeople(message, username)
            } else if (message.send_type == 'switch') {
                // switch chats
                switchChat(JSON.parse(message.chat))
            } else if (message.send_type == 'load') {
                // load chats
                console.log("...loading chats...");
                loadChats(message, username);
            } else if(message.send_type == 'load_messages') {
                // load messages
                console.log("pk: " + message.pk);
                loadChatMessages(message, username)
            }
        };
        this.socket.onclose = function(e) {
            console.log('Chat socket closed unexpectedly');
        };
    }

    sendMessage(msg) {
        this.socket.send(JSON.stringify({
            'send_type': 'chat_message',
            'message': msg,
        }));
    }

    findChat(newChatMembers) {
        this.socket.send(JSON.stringify({
            'send_type': 'find_create',
            'participants': newChatMembers
        }));
    }
};
