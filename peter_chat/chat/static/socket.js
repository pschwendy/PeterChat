
const roomName = JSON.parse(document.getElementById('room-name').textContent);
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
    </div>'

chatSocket.onmessage = function(msg){
    const message = JSON.parse(msg.data);
    console.log(message.send_type)
    if (message.send_type == 'chat') {
        //const _id = JSON.parse(id.data);
        //if(message.id == chatSocket.id) {
        msgHtml = '<div class="message-row sent-message">\
                <div class="message-content">\
                <div class="message-text">'
        //}
        //else{
            /*msgHtml = '<div class="message-row received-message">\
                <div class="message-content">\
                    <img src="th.jpg" alt="Katya Schwendeman" class="profile-pic">\
                    <div class="message-text">'*/
        //}
        /*msgHtml = '<div class="message-row sent-message">\
            <div class="message-content">\
            <div class="message-text">'*/
        /*if(message.indexOf("/shrug") != -1) {
            message = "¯\\_(ツ)_/¯";
        } else if (message.indexOf("/facepalm") != -1){
            message = "(—‸ლ)";
        }*/
        var endOfContainer = '';
        //var today = new Date();
        //var time = today.getHours() + ":" + today.getMinutes();
        endOfContainer = timeHtml + timeHtml + timeHtmlEng + containerEnd;
        $('#conversation').prepend(msgHtml + message.message + msgHtmlEnd + endOfContainer);
        $('#recent-message').text(message.message);
    }
    else if (message.send_type == 'search') {
        console.log("hi");
        document.getElementById('searches').textContent = '';
        const users = JSON.parse(message.users);
        for(var i = 0; i < users.length; ++i) {
            console.log(users[i].fields.username);
            const usernameReceived = users[i].fields.username;
            const idReceived = users[i].fields.pk;
            const user = users[i];
            var userDiv = document.createElement("div");
            userDiv.className = "chat inherit";
            if(newChatMembers.indexOf(idReceived) != -1){
                userDiv.className += " selected";
            }
            var userImg = document.createElement("img");
            userImg.src = "{% 'th.jpg' %}";
            userImg.alt = "Katya Schwendeman";
            userImg.className = "profile-pic";

            var usernameDiv = document.createElement("div");
            usernameDiv.className = "chat-name";
            usernameDiv.innerHTML = users[i].fields.username;

            var active = document.createElement("div");
            active.className = "recent-message";
            active.innerHTML = "Active Dec 10";

            userDiv.appendChild(userImg);
            userDiv.appendChild(usernameDiv);
            userDiv.appendChild(active);

            userDiv.onclick = function(){
                if(userDiv.className.indexOf("selected") != -1) {
                    userDiv.className = "chat inherit";
                    document.getElementById(idReceived + "button").remove();
                    return;
                }
                userDiv.className += " selected";
                $('#searcher').val('');
                
                var addedUser = document.createElement("button");
                addedUser.className = "added-user btn";
                addedUser.id = idReceived + "button";

                var addedName = document.createElement("span");
                addedUser.innerHTML = usernameReceived;

                var close = document.createElement("i");
                close.className = "fa fa-times"
                close.onclick = function() {
                    for (var i = 0; i < newChatMembers.length; ++i) {
                        if(newChatMembers[i].fields.pk == idReceived) {
                            newChatMembers.splice(i, i + 1);
                        }
                    };
                    document.getElementById(idReceived + "button").remove();
                    userDiv.className = "chat inherit";
                };

                addedUser.appendChild(addedName);
                addedName.appendChild(close);

                $("#search-for").prepend(addedUser);
                newChatMembers.push(user);
            };

            const userHtml = '<div class="chat"> \
                <img src="';
            const source = "{% static 'th.jpg' %}";
            const midHtml = '" alt="Katya Schwendeman" class="profile-pic"> \
                <div class="chat-name">';
            const userHtmlEnd	= '</div> \
                <div class="recent-message">Active Dec 10</div> \
                </div>';

            //$('#searches').append(userHtml + source + midHtml + users[i].fields.username + userHtmlEnd);
            $('#searches').append(userDiv);
        }
    }
    else if (message.send_type == 'switch') {
        // switch url to chat
    } 
    //console.log(message.length)
    /**/
};
chatSocket.onclose = function(e) {
    console.log('Chat socket closed unexpectedly');
};
chatSocket.onopen = function(e) {
    chatSocket.send(JSON.stringify({
        'send_type': 'authenticate',
        'username': username,
    }));
};