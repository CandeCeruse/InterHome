$(document).ready(function() {
    getData();
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
            // Actualizar gráficos de temperatura y humedad
            updateTemperatureChart(id, temperatura, humedad);
        }        
    });
}

// Función para actualizar el gráfico de temperatura
function updateTemperatureChart(id, temperatura, humedad) {
    const ctx = document.getElementById('temperatureChart' + id).getContext('2d');
    const config = {
        type: 'bar',
        data: {
            labels: [
                'Temperatura',
                'Humedad'
            ],
            datasets: [{
                label: 'Temperatura y Humedad',
                data: [temperatura, humedad],
                backgroundColor:[
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)'
            
                ],
                hoverOffset: 4
            }]
        },
        options: {
            scales: {
              y: {
                beginAtZero: true
              }
            }
          },
    };
    new Chart(ctx, config);
}

function toggleState(checkbox) {
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
