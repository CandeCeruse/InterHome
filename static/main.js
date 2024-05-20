$(document).ready(function() {
    getData();
    setLightButtonState();
    // Llamar funcion que consiga los estados de los dispositivos (on/off de las luces).
    // Recargar la página cada 5 segundos
    setInterval(function(){
        window.location.reload();
    }, 10000);
});

//Esta funcion recolecta los datos de los sensores de temperatura solamente,
//Y envia la informacion de lo recolectado en formato JSON,
// {'temperature': 37, 'humidity': 11, 'MAC': 'E8:DB:84:E5:08:96', 'device_id': 1}
function getData() {
    const Url = "/temperature";
    $.ajax({
        url: Url,
        type: "GET",
        success: function(data) {
            var id = data.device_id;
            var temperatura = data.temperature;
            var humedad = data.humidity;
            //var label = data.label;
            // Actualizar gráficos de temperatura y humedad
            //updateTemperatureChart(id, temperatura, humedad);
            dmbChart(300, humedad, temperatura, id);
        }        
    });
}

function setLightButtonState() {
    const Url = "/state/light";
    $.ajax({
        url: Url,
        type: "GET",
        success: function(data) {
            console.log(data);
            // Itera sobre las claves del objeto 'data'
            Object.keys(data).forEach(function(deviceId) {
                // Obtiene el estado del dispositivo por su ID
                var deviceState = data[deviceId].state;
                // Genera el ID del botón basado en el ID del dispositivo
                var buttonId = "toggleButton" + deviceId;
                // Selecciona el botón por su ID
                var $button = $("#" + buttonId);
                // Actualiza el estado del botón basado en el estado enviado desde el servidor
                $button.prop('checked', deviceState === 'ON');
            });
        }        
    });
}

function dmbChart(scale, percent, temp, id) {
    var ctx = document.getElementById('temperatureChart' + id).getContext('2d');
    var cx = scale / 2;
    var cy = scale / 2;
    var radius = scale * 0.375;
    var PI2 = Math.PI * 2;
    var up = Math.PI * -0.5;
    var angle = up + PI2 * percent / 100;
    var fontsize = scale * 0.225

    ctx.lineWidth = scale * 0.2;
  
    ctx.beginPath();
    ctx.shadowblur = 1;
    ctx.shadowcolor = "black";
    ctx.shadowOffsetX = 25;
    ctx.arc(cx, cy, radius, 0, PI2);
    ctx.strokeStyle = "gray";
    ctx.stroke();
  
    ctx.beginPath();
    ctx.shadowblur = 1;
    ctx.shadowcolor = "black";
    ctx.shadowOffsetX = 25;
    ctx.arc(cx, cy, radius * 0.9, 0, PI2);
    ctx.strokeStyle = "darkgray";
    ctx.stroke();
    
    ctx.beginPath();
    ctx.shadowblur = 1;
    ctx.shadowcolor = "black";
    ctx.shadowOffsetX = 25;
    ctx.strokeStyle = "lightseagreen";
    ctx.arc(cx, cy, radius, up, angle);
    ctx.stroke();
  
    ctx.beginPath();
    ctx.shadowblur = 1;
    ctx.shadowcolor = "black";
    ctx.shadowOffsetX = 25;
    ctx.arc(cx, cy, radius * 0.9, up, angle);
    ctx.strokeStyle = "turquoise";
    ctx.stroke();
    
  
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'darkcyan';
    ctx.font = (fontsize) + 'px trebuchet ms';
    ctx.fillText(percent + "%", cx, cy);
    
    ctx.textAlign = 'right';
    ctx.fillStyle = 'darkorange';
    ctx.font = (fontsize * 2) + 'px trebuchet ms';
    ctx.fillText(temp, cx + 3 * radius, cy);
    ctx.textAlign = 'left';
    ctx.font = (fontsize * 2) + 'px tahoma';
    ctx.fillText('°C', cx + 3 * radius, cy);
}

function toggleState(checkbox) {
    console.log(checkbox);
    var id = checkbox.getAttribute('device'); // Aquí puedes establecer el ID que deseas enviar al servidor
    var mac = checkbox.getAttribute('mac'); // Obtiene la dirección MAC del dispositivo
    var state = checkbox.checked ? 'ON' : 'OFF';
    sendData(id, mac, state);
}

function sendData(id, mac, state){
    console.log("Ingreso con el id", id, "MAC", mac, "estado", state);
    const Url = "/light";
    $.ajax({
        url: Url,
        type: 'POST',
        contentType: 'application/json', // Especifica que el contenido es JSON
        data: JSON.stringify({topic: "light", id: id, mac: mac, state: state}), // Convierte los datos a JSON
        success: function (data) {
            console.log('Response:', data);
        },
        error: function(xhr, status, error) {
            console.error('Error', error);
        }
    });
}
