function get_data(){
    // Create a request variable and assign a new XMLHttpRequest object to it.
    var request = new XMLHttpRequest()

    // Open a new connection, using the GET request on the URL endpoint
    request.open('GET', 'https://api.thingspeak.com/channels/1320809/feeds.json?results=60', true)

    request.onload = function () {
    
        // Begin accessing JSON data here
        var data = JSON.parse(this.response);
		console.log(data.feeds);
		var length = data.feeds.length;
		var lastVal = data.feeds[length-1];
		if (lastVal.field1 != null){
			var lux = lastVal.field1;
			var temp = lastVal.field2;
			var hum = lastVal.field3;
		}
		else{
			var lux = data.feeds[length-2];
			var temp = data.feeds[length-2];
			var hum = data.feeds[length-2];
		}
			
		if(data.feeds[length-1].field4 == 1 && data.feeds[length-2].field4 == 1 && data.feeds[length-3].field4 == 1)
				var active = 1;
		if(data.feeds[length-1].field4 == 0 && data.feeds[length-2].field4 == 0 && data.feeds[length-3].field4 == 0)
				var active = 0;
		var i;
		for (i = 0; i < length; i++) {
			if (data.feeds[i].field5 != null){
				dist = data.feeds[i].field5;
				pulses = data.feeds[i].field7;
			}
		}
		
        var textDiv = document.getElementById("bio-text");
		var conditions = "<p>Temperatura interna: "+temp+"°</p><p>Umidità relativa: "+hum+"%</p><p>Livello di luce: "+lux+" lux</p>";
		if (active == 1)
			activity = "<br>Bit è sveglio in questo momento<br>"
		else
			activity = "<br>Bit sta dormendo in questo momento<br>"
		var wheelInfo = "<br>Bit ha percorso "+dist+" metri e compiuto "+pulses+" giri nella sua ruota a partire dalle 8 del mattino.<br>"
        textDiv.innerHTML = conditions + activity + wheelInfo;
       
    }

    // Send request
    request.send()
    
}

document.addEventListener('DOMContentLoaded', function() {
    get_data();
	var intervalId = window.setInterval(function(){
		get_data();
	}, 60000);
}, false);