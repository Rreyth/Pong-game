import * as test from './game/test.js'

test.yeet()

// debut du client

// var game = Game()

var GameHub = new WebSocket("ws://localhost:6669")

var GameRoom = false

GameHub.onerror = function(error) {
	console.error("Connection failed: ", error)
}

GameHub.onopen = function() {
	try_connect()
	in_game()
}

GameHub.onclose = function() {
	console.log("Connection closed")
}

GameHub.onmessage = function(event) {
	var msg = JSON.parse(event.data)
	if (msg.type == "connectionRpl") {
		if (msg.success == "true") {
			console.log("Connection success")
			// game.alias = msg.alias
		} else {
			console.log("Connection failed") //return to home or smth ?
		}
	}
}

function try_connect() {
	var msg = {"type" : "connect", "cmd" : "token"}
	GameHub.send(JSON.stringify(msg))
}

function in_game() {
	game.start(GameHub)
}



// socket.onmessage = parsefct
// Et ta fonction sera lancée en asynchrone dès que tu reçois un message dans le websocket
// , c'est en asynchrone, donc pas à chaque tic, sa se lance instant dès que le msg est là... Se qui permet de traiter plusieurs message en même temps
// Dès que ton websocket est défini, ou dépendamment de comment tu fait ton JS...
// En gros, tu dis juste à ton websocket si je reçoit un message, je lance cette fonction...


// tu ne peut pas utiliser une boucle while (ou for) pour faire ta boucle principale de jeu, sinon, 
// ton navigateur va au mieux considérer que la fenêtre prend trop de ressources et te demander si tu veux la stopper, 
// ou au pire juste freeze jusqu'à ce que tu ferme ton onglet.... (même avec un sleep dans le while)

// Pour réglé le problème, tu créé une fonction qui fait tout ce que ton jeu dois faire dans un tick, et tu lance cette fonction dans un setinterval :

//                 var toninterval = setInterval(tafonctionalancer, tonintervaldetemps )


// Si tu veux arrêter l'interval :
//                                clearInterval(interval);


// Pour l'unité de temps utilisé par setinterval, je m'en souviens plus, faudra chercher.