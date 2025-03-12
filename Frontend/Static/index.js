// Acceder a la webcam
const video = document.getElementById("webcam");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
let stream = null; // Variable para almacenar el stream de la webcam

// Función para detener el stream de la webcam
function stopWebcam() {
    if (stream) {
        stream.getTracks().forEach(track => {
            track.stop();
        });
        stream = null;
    }
}

// Iniciar la transmisión de la webcam
async function startWebcam() {
    try {
        // Detener cualquier stream previo
        stopWebcam();
        
        // Solicitar un nuevo stream
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: true,
            audio: false
        });
        
        // Asignar el stream al elemento de video
        video.srcObject = stream;
        
        // Esperar a que el video esté listo
        await new Promise(resolve => {
            video.onloadedmetadata = () => {
                resolve();
            };
        });
        
        console.log("Webcam iniciada correctamente");
    } catch (err) {
        console.error("Error al acceder a la cámara", err);
        alert("No se pudo acceder a la cámara. Por favor, asegúrate de que tienes una cámara conectada y has dado permiso para usarla.");
    }
}

// Iniciar la webcam cuando se carga la página
document.addEventListener('DOMContentLoaded', async () => {
    console.log("Página index cargada, iniciando webcam...");
    
    // Limpiar cualquier resultado anterior al cargar la página
    try {
        await fetch('/clear_data', {
            method: 'POST',
        });
        console.log("Datos anteriores limpiados correctamente");
    } catch (error) {
        console.error("Error al limpiar datos anteriores:", error);
    }
    
    // Iniciar la webcam después de un pequeño retraso
    setTimeout(startWebcam, 300);
});

// Capturar la imagen cuando se haga clic en el botón
document.getElementById("capturar-btn").addEventListener("click", async () => {
    try {
        // Verificar que el video está listo
        if (!video.videoWidth) {
            alert("La cámara no está lista. Por favor, espera un momento.");
            return;
        }

        // Ajustar el tamaño del canvas según el tamaño del video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Dibujar el frame actual del video en el canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Obtener la imagen en formato base64 (data URL)
        const imageData = canvas.toDataURL("image/jpeg", 0.9); // Use JPEG with 90% quality for smaller size

        console.log("Imagen capturada, tamaño:", imageData.length);

        // Detener la webcam antes de navegar a otra página
        stopWebcam();
        
        // Mostrar pantalla de carga antes de enviar la imagen
        window.location.href = "/carga";
        
        // Enviar la imagen al servidor en segundo plano
        fetch('/process_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del servidor:", data);
            if (!data.success) {
                console.error("Error en el procesamiento:", data.error);
            }
        })
        .catch(error => {
            console.error('Error en segundo plano:', error);
        });
        
    } catch (error) {
        console.error('Error al capturar la imagen:', error);
        alert('Error al preparar la imagen. Por favor, inténtalo de nuevo.');
    }
});

// Manejar la visibilidad de la página para reiniciar la webcam cuando se vuelve a la página
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log("Página visible nuevamente, reiniciando webcam...");
        setTimeout(startWebcam, 300);
    } else {
        console.log("Página oculta, deteniendo webcam...");
        stopWebcam();
    }
});

// Asegurarse de que se liberen los recursos cuando se cierra la página
window.addEventListener('beforeunload', () => {
    stopWebcam();
});
