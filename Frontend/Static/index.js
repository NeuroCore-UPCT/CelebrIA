// Acceder a la webcam
const video = document.getElementById("webcam");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

// Iniciar la transmisión de la webcam
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error al acceder a la cámara", err);
        alert("No se pudo acceder a la cámara. Por favor, asegúrate de que tienes una cámara conectada y has dado permiso para usarla.");
    }
}

startWebcam();

// Capturar la imagen cuando se haga clic en el botón
document.getElementById("capturar-btn").addEventListener("click", async () => {
    // Ajustar el tamaño del canvas según el tamaño del video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Dibujar el frame actual del video en el canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Obtener la imagen en formato base64 (data URL)
    const imageData = canvas.toDataURL("image/png");

    try {
        // Limpiar cualquier resultado anterior
        await fetch('/clear_data', {
            method: 'POST',
        });
        
        // Mostrar pantalla de carga antes de enviar la imagen
        // Esto evita que se muestre un error si la petición tarda en procesarse
        window.location.href = "/carga";
        
        // Enviar la imagen al servidor en segundo plano
        // No esperamos la respuesta aquí, la página de carga se encargará de comprobar el estado
        fetch('/process_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        }).catch(error => {
            console.error('Error en segundo plano:', error);
            // No mostramos alerta aquí porque ya estamos en la página de carga
        });
        
        // No esperamos la respuesta aquí, la página de carga se encargará de comprobar el estado
    } catch (error) {
        console.error('Error:', error);
        alert('Error al preparar la imagen. Por favor, inténtalo de nuevo.');
        // No redirigimos en caso de error para que el usuario pueda intentarlo de nuevo
    }
});
