$(document).ready(function() {
    // Carga los nombres de los dispositivos desde el almacenamiento local
    $('.device-label').each(function() {
        let deviceId = this.id.split('-')[1];
        let storedName = localStorage.getItem('deviceName-' + deviceId);
        if (storedName) {
            $(this).text(storedName);
        }
    });

    // Evento click para los labels
    $('.device-label').click(function(event) {
        event.stopPropagation(); // Prevenir que el evento se propague al checkbox
        let deviceId = this.id.split('-')[1];
        nombrarDispositivo(deviceId);
    });

    function setLabels() {
        const Url = "/set/label";
        $.ajax({
            url: Url,
            type: "GET",
            success: function(data) {
                // Itera sobre los datos recibidos y actualiza el nombre de cada label
                data.forEach(function(device) {
                    // Encuentra el label correspondiente y actualiza su texto
                    $('#label-' + device.id).text(device.name);
                });
            }
        });
    }

    // El resto de tu código JavaScript va aquí...
    // Por ejemplo:
    setLabels();
    getData();
    setLightButtonState();
    setInterval(function(){
        window.location.reload();
    }, 10000);
});

function nombrarDispositivo(deviceId) {
    let texto;
    let nombreDispositivo = prompt("Ingrese el nombre del dispositivo: ");
    if (nombreDispositivo == null || nombreDispositivo == "") {
        nombrarDispositivo(deviceId);
    } else {
        texto = nombreDispositivo;
        document.getElementById("label-" + deviceId).innerText = texto;
        localStorage.setItem('deviceName-' + deviceId, texto); // Guarda el nuevo nombre en el almacenamiento local
        // Actualizar el nombre en el diccionario de dispositivos en el servidor
        $.ajax({
            url: "/update-device-name",
            type: 'POST',
            contentType: 'application/json', // Especifica que el contenido es JSON
            data: JSON.stringify({name: texto, id: deviceId}),
            success: function(data) {
                console.log('Response:', data); // Manejo de respuesta exitosa
            },
            error: function(error) {
                console.error('Error al actualizar el nombre del dispositivo:', error);
            }
        });
    }
}


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
            dmbChart(300, humedad, temperatura, id);
            // Cambiar la imagen basado en la temperatura
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
    var ctz = document.getElementById('humedadChart' + id).getContext('2d');
    var img = new Image();
    var cx = scale / 2;
    var cy = scale / 2;
    var radius = scale * 0.375;
    var PI2 = Math.PI * 2;
    var up = Math.PI / -2;
    var angle = up + PI2 * percent / 100;
    var fontsize = scale * 0.45;

    ctx.lineWidth = scale * 0.2;
    ctx.shadowBlur = 5;
    ctx.shadowColor = "rgba(150, 150, 150, 0.5)";
    ctx.shadowOffsetX = 7;
    ctz.shadowBlur = 5;
    ctz.shadowColor = "rgba(65, 65, 65, 0.5)";
    ctz.shadowOffsetX = 7;

    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, PI2);
    ctx.strokeStyle = "gray";
    ctx.stroke();
  
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.9, 0, PI2);
    ctx.strokeStyle = "darkgray";
    ctx.stroke();
  
    // Dibujar semicírculo verde claro
    ctx.save(); // Guardar estado actual
    ctx.beginPath();
    ctx.shadowBlur = 5;
    ctx.shadowColor = "rgba(150, 150, 150, 0.5)";
    ctx.shadowOffsetX = 7;
    ctx.strokeStyle = "lightseagreen"; //darkcyan lightseagreen
    ctx.arc(cx, cy, radius, up, angle);
    ctx.stroke();
    ctx.restore(); // Restaurar estado anterior

    // Dibujar semicírculo turquesa claro
    ctx.save(); // Guardar estado actual
    ctx.beginPath();
    ctx.shadowBlur = 5;
    ctx.shadowColor = "rgba(150, 150, 150, 0.5)";
    ctx.shadowOffsetX = 7;
    ctx.strokeStyle = "turquoise"; //turquoise
    ctx.arc(cx, cy, radius * 0.9, up, angle);
    ctx.stroke();
    ctx.restore(); // Restaurar estado anterior

    var fontsize = scale * 0.225;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'darkcyan';
    ctx.font = (fontsize) + 'px trebuchet ms';
    ctx.fillText(percent + "%", cx, cy);

    //Dibujar medida de temperatura
    if (temp < 10){
        //document.getElementById('snowImage').src = "{{ url_for('static', filename='/imagenes/snow.png') }}";
        document.getElementById('snowImage').style.display = "block";
        document.getElementById('fireImage').style.display = "none";
        ctz.fillStyle = 'darkblue';
    }
    else{
        //document.getElementById('fireImage').src = "{{ url_for('static', filename='/imagenes/fire.png') }}";
        document.getElementById('fireImage').style.display = "block";
        document.getElementById('snowImage').style.display = "none";
        ctz.fillStyle = 'darkorange';
    }
    ctz.drawImage(img, 0, 0, scale, scale); //Reemplazar tercer argumento con: cy - scale * 0.8
    ctz.textAlign = 'right';
    ctz.font = (fontsize * 2) + 'px trebuchet ms';
    ctz.fillText(temp, cx, cy+27);
    ctz.textAlign = 'left';
    ctz.font = (fontsize * 2) + 'px tahoma';
    ctz.fillText('°C', cx, cy+27);
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