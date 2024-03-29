// Class for managing chat web sockets
class ChatSocket {
    // constructor
    // connects to websocket given room name
    // input: roomName -> chat room (id)
    // input: username -> logged in user's username
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
            if (message.send_type == 'chat') {
                // load message
                loadMessage(message, username);
            } else if (message.send_type == 'new_messages') {;
                updateChatList(message);
            } else if (message.send_type == 'search') {
                // display people
                findPeople(message, username);
            } else if (message.send_type == 'switch') {
                // switch chats
                switchChat(JSON.parse(message.chat));
            } else if (message.send_type == 'load') {
                // load chats
                console.log("...loading chats...");
                loadChats(message, username, roomName);
            } else if(message.send_type == 'load_messages') {
                this.fetchingMessages = false;
                // load messages
                console.log("pk: " + message.pk);
                loadChatMessages(message, username);
            }
        };
        this.fetchingMessages = false;
        this.threshold = 1;
        this.socket.onclose = function(e) {
            console.log('Chat socket closed unexpectedly');
        };
    } // constructor

    // send message to server
    // input: msg -> message being sent
    sendMessage(msg) {
        this.socket.send(JSON.stringify({
            'send_type': 'chat_message',
            'message': msg,
        }));
    } // sendMessage

    // tells server to find/create chat given members
    // input: newChatMembers -> members being searched
    findChat(newChatMembers) {
        this.socket.send(JSON.stringify({
            'send_type': 'find_create',
            'participants': newChatMembers
        }));
    } // findChat
    
    fetchMessages() {
        this.socket.send(JSON.stringify({
            'send_type': 'fetch_messages'
        }));
        this.fetchingMessages = true;
    }

    stopFetching() {
        this.fetchingMessages = false;
        this.threshold *= 6/5;
    }
    // useless function LOL
    updateSocket(roomName) {
        this.socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + roomName
            + '/'
        );
    }
}; // ChatSocket
