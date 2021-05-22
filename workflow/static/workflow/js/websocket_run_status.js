const RUN_STATUS_ID = document.getElementById('websocket_run_status').getAttribute('run_id');
var run_status_cell = document.getElementById('run_status_cell')

// open the websocket
var ws_url = 'ws://' + window.location.host + '/ws/run-status/' + RUN_STATUS_ID + '/';
var statusSocket = new WebSocket(ws_url);

statusSocket.onmessage = function(event) {
    var data = JSON.parse(event.data);
    console.log('WebSocket message received:', event);
    run_status_cell.innerHTML = data[0].run_status
};

statusSocket.onopen = function open() {
    console.log('Websocket connection for run ' + RUN_STATUS_ID + ' status created.');
};

if (statusSocket.readyState == WebSocket.OPEN) {
    console.log('Opening WebSocket');
    statusSocket.onopen();
}

