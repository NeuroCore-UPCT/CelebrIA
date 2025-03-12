// Mostrar la pantalla de carga durante un tiempo determinado
// y luego redirigir a la página de resultados

// Variable para controlar el tiempo máximo de espera (en milisegundos)
const MAX_WAIT_TIME = 120000; // 120 segundos (2 minutos)
let startTime = Date.now();
let processingComplete = false;
let processingStarted = false;
let consecutiveWaitingCount = 0;

// Función para comprobar si el procesamiento ha terminado
async function checkProcessingStatus() {
    try {
        // Si ha pasado el tiempo máximo de espera, mostrar un mensaje de error
        if (Date.now() - startTime > MAX_WAIT_TIME) {
            showError("El procesamiento está tardando demasiado. Por favor, inténtalo de nuevo.");
            return;
        }
        
        // Comprobar el estado del procesamiento
        const response = await fetch('/process_status');
        const data = await response.json();
        
        console.log("Estado del procesamiento:", data);
        
        // Actualizar el mensaje de carga según el estado
        updateLoadingMessage(data.message);
        
        if (data.status === 'complete') {
            // Si el procesamiento ha terminado, redirigir a la página de resultados
            processingComplete = true;
            window.location.href = "/resultado";
            return;
        } else if (data.status === 'error') {
            // Si ha habido un error, mostrar el mensaje de error
            showError(data.message);
            return;
        } else if (data.status === 'processing') {
            // Si el procesamiento ha comenzado, actualizar la bandera
            processingStarted = true;
            consecutiveWaitingCount = 0;
        } else if (data.status === 'waiting') {
            // Si seguimos esperando, incrementar el contador
            consecutiveWaitingCount++;
            
            // Si hemos estado esperando demasiado tiempo (más de 10 segundos)
            if (consecutiveWaitingCount > 10) {
                showError("No se ha recibido la imagen. Por favor, vuelve e intenta capturar la foto de nuevo.");
                return;
            }
        }
        
        // Si el procesamiento sigue en curso, comprobar de nuevo después de un tiempo
        setTimeout(checkProcessingStatus, 1000);
    } catch (error) {
        console.error('Error al comprobar el estado del procesamiento:', error);
        // En caso de error, intentar de nuevo después de un tiempo
        setTimeout(checkProcessingStatus, 2000);
    }
}

// Función para actualizar el mensaje de carga
function updateLoadingMessage(message) {
    const loadingText = document.querySelector('.loading-text');
    if (loadingText && message) {
        loadingText.textContent = message;
    }
}

// Función para mostrar un mensaje de error
function showError(message) {
    const loadingSpinner = document.querySelector('.loading-spinner');
    const loadingText = document.querySelector('.loading-text');
    
    if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
    }
    
    if (loadingText) {
        loadingText.textContent = message;
        loadingText.style.color = 'red';
    }
    
    // Añadir un botón para volver a la página principal
    const container = document.querySelector('.rectangulo');
    if (container) {
        // Si ya existe un botón, no crear otro
        if (!document.querySelector('.back-button')) {
            const backButton = document.createElement('button');
            backButton.textContent = 'Volver a intentar';
            backButton.className = 'back-button';
            backButton.onclick = () => {
                // Redirigir con parámetro de tiempo para forzar recarga
                window.location.href = '/?reload=' + new Date().getTime();
            };
            container.appendChild(backButton);
        }
    }
}

// Iniciar la comprobación del estado del procesamiento
document.addEventListener('DOMContentLoaded', () => {
    console.log("Página de carga iniciada");
    // Esperar un poco antes de empezar a comprobar
    setTimeout(checkProcessingStatus, 1000);
});