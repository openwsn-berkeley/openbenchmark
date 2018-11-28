var app = require('express')();
var server = require('http').Server(app);
var io = require('socket.io')(server);

server.listen(3000);
var channelId = 1;

io.on('connection', function(socket) {
	console.log('A connection was made!');

	socket.on('channelRegistration', id => {
		socket.join('channel' + id);
		console.log('A channel has been registered: channel' + id);
	});

	socket.on('NODE_RESERVATION', message => {
		console.log('Topic: NODE_RESERVATION - ' + message);
		io.to('channel' + channelId).emit('NODE_RESERVATION', message)
	});
    socket.on('RESERVATION_SUCCESS', message => {
        console.log('Topic: RESERVATION_SUCCESS - ' + message);
        io.to('channel' + channelId).emit('RESERVATION_SUCCESS', message)
    });
    socket.on('RESERVATION_STATUS_RETRY', message => {
        console.log('Topic: RESERVATION_STATUS_RETRY - ' + message);
        io.to('channel' + channelId).emit('RESERVATION_STATUS_RETRY', message)
    });
    socket.on('RESERVATION_FAIL', message => {
        console.log('Topic: RESERVATION_FAIL - ' + message);
        io.to('channel' + channelId).emit('RESERVATION_FAIL', message)
    });

	socket.on('NODE_BOOTED', message => {
		console.log('Topic: NODE_BOOTED - ' + message);
		io.to('channel' + channelId).emit('NODE_BOOTED', message)
	});
    socket.on('BOOT_RETRY', message => {
        console.log('Topic: BOOT_RETRY - ' + message);
        io.to('channel' + channelId).emit('BOOT_RETRY', message)
    });
    socket.on('BOOT_FAIL', message => {
        console.log('Topic: BOOT_FAIL - ' + message);
        io.to('channel' + channelId).emit('BOOT_FAIL', message)
    });

    socket.on('NODE_ACTIVE', message => {
		console.log('Topic: NODE_ACTIVE - ' + message);
		io.to('channel' + channelId).emit('NODE_ACTIVE', message)
	});
    socket.on('NODE_ACTIVE_FAIL', message => {
        console.log('Topic: NODE_ACTIVE_FAIL - ' + message);
        io.to('channel' + channelId).emit('NODE_ACTIVE_FAIL', message)
    });

    socket.on('LOG_MODIFICATION', message => {
        console.log('Topic: LOG_MODIFICATION - ' + message);
        io.to('channel' + channelId).emit('LOG_MODIFICATION', message)
    });

    socket.on('EXP_TERMINATE', message => {
        console.log('Topic: EXP_TERMINATE - ' + message);
        io.to('channel' + channelId).emit('EXP_TERMINATE', message)
    });
});