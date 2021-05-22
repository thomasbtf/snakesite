const RUN_ID = document.getElementById('websocket_run_messages').getAttribute('run_id');

// open the websocket
var ws_url = 'ws://' + window.location.host + '/ws/messages/' + RUN_ID + '/';
var messagesSocket = new WebSocket(ws_url);

messagesSocket.onmessage = function(event) {
    var data = JSON.parse(event.data);
    // console.log('Run Message WebSocket message received:', event);
    addRows(data)
};

messagesSocket.onopen = function open() {
    console.log('Websocket connection for run ' + RUN_ID + ' messages created.');
};

if (messagesSocket.readyState == WebSocket.OPEN) {
    console.log('Opening WebSocket');
    messagesSocket.onopen();
}

function clear_undefined(data) {
    if( typeof data !== 'undefined' ) {
        return data
    }
    return ""
}


function addRows(data) {
    // Find a <table> element with id="myTable":
    var table = document.getElementById('messageTable').getElementsByTagName('tbody')[0];

    // Create an empty <tr> element and add it to the 1st position of the table:
    var row1 = table.insertRow(0);
    var row2 = table.insertRow(1);
    var row3 = table.insertRow(2);
    var row4 = table.insertRow(3);

    // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
    var cell11 = row1.insertCell(0);
    var cell12 = row1.insertCell(1);
    var cell13 = row1.insertCell(2);
    var cell14 = row1.insertCell(3);

    var cell21 = row2.insertCell(0);
    var cell22 = row2.insertCell(1);
    var cell23 = row2.insertCell(2);
    var cell24 = row2.insertCell(3);

    var cell31 = row3.insertCell(0);
    var cell32 = row3.insertCell(1);
    var cell33 = row3.insertCell(2);
    var cell34 = row3.insertCell(3);

    var cell41 = row4.insertCell(0);
    var cell42 = row4.insertCell(1);
    var cell43 = row4.insertCell(2);
    var cell44 = row4.insertCell(3);

    // Add some text to the new cells:
    cell11.innerHTML = data[0].timestamp;
    cell12.innerHTML = data[1].level;
    cell13.outerHTML = "<th>Job</th>";
    cell14.innerHTML = clear_undefined(data[1].job);

    cell23.outerHTML = "<th>Status</th>";
    cell24.innerHTML = clear_undefined(data[1].status);

    cell33.outerHTML = "<th>Message</th>";
    cell34.innerHTML = clear_undefined(data[1].error) + " " + clear_undefined(data[1].msg);
    cell34.style = "word-break:break-all;";

    cell43.outerHTML = "<th>File</th>";
    cell44.innerHTML = clear_undefined(data[1].status);
}
