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
    }
}

startWebcam();

// Capturar la imagen cuando se haga clic en el botón
document.getElementById("capturar-btn").addEventListener("click", () => {
    // Ajustar el tamaño del canvas según el tamaño del video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Dibujar el frame actual del video en el canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Obtener la imagen en formato base64 (data URL)
    const imageData = canvas.toDataURL("image/png");

    // Guardar la imagen en localStorage (esto es temporal y no es un archivo físico)
    localStorage.setItem("captura", imageData);

    // Redirigir a la siguiente página (sin mostrar la imagen)
    window.location.href = "../Templates/carga.html";
});
