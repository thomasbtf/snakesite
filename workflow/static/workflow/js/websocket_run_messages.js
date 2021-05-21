var run_id = document.getElementById("socket_script").getAttribute("run_id");

// open the websocket
var ws_url = 'ws://' + window.location.host + '/ws/messages/' + run_id + '/';
var messagesSocket = new WebSocket(ws_url);

messagesSocket.onmessage = function(event) {
    var data = JSON.parse(event.data);
    console.log("WebSocket message received:", event);
    addRows()
};

messagesSocket.onopen = function open() {
    console.log('WebSocket connection created.');
};

if (messagesSocket.readyState == WebSocket.OPEN) {
    console.log("Opening WebSocket");
    messagesSocket.onopen();
}

function addRows() {
    var table = document.getElementById( 'messageTable' ),
        row = table.insertRow(0),
        cell1 = row.insertCell(0),
        cell2 = row.insertCell(1);

    cell1.innerHTML = 'Cell 1';
    cell2.innerHTML = 'Cell 2';
}