const RUN_PROGRESS_ID = document.getElementById('websocket_run_progress').getAttribute('run_id');

// open the websocket
var ws_url = 'ws://' + window.location.host + '/ws/run-progress/' + RUN_PROGRESS_ID + '/';
var progressSocket = new WebSocket(ws_url);

progressSocket.onmessage = function(event) {
    var data = JSON.parse(event.data);
    console.log('Progress got data', data)
    // console.log('Run Message WebSocket message received:', event);
    updateProgress(data)
};

progressSocket.onopen = function open() {
    console.log('Websocket connection for run ' + RUN_PROGRESS_ID + ' progress created.');
};

if (progressSocket.readyState == WebSocket.OPEN) {
    console.log('Opening WebSocket');
    progressSocket.onopen();
}

function clear_undefined(data) {
    if( typeof data !== 'undefined' ) {
        return data
    }
    return ""
}

function updateProgress(data){
    var run_progress_cell = document.getElementById('run_progress_cell')
    run_progress_cell.innerHTML = data[0].run_progress + "%"
}