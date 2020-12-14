var app = require('express')();
var express = require('express');
var http = require('http').Server(app);

//const io = require('socket.io-client')(http);
var url = require('url');
var fs = require('fs');

app.get('/', function(req, res){
	res.sendfile('peter_chat.html');
});
app.use(express.static("static-files"));

server = app.listen(3000, function(){
	console.log('listening on *:3000')
});
var io = require('socket.io').listen(server);
io.on('connection', function(socket) {
	socket.on('sendMessage', function(msg) {
      io.sockets.emit('sendMessage', msg, socket.id);
   });
});
