var num_personas ; //El número de personas que aparecen el la fotografía
var n; //variable para el bucle for
let imagen ; //arreglo para las imágenes

// Script para mostrar los resultados en la página de resultados

document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log("Página de resultados cargada, obteniendo resultados...");
        
        // Obtener los resultados del servidor
        const response = await fetch('/get_results');
        const data = await response.json();
        
        console.log("Respuesta del servidor:", data);
        
        if (!data.success) {
            console.error('Error en la respuesta:', data.error);
            alert('Error al obtener resultados. Volviendo a la página principal...');
            window.location.href = '/';
            return;
        }
        
        // Hacer una copia de los resultados para evitar modificaciones accidentales
        const results = JSON.parse(JSON.stringify(data.results || []));
        
        if (!results || results.length === 0) {
            console.error('No se encontraron resultados.');
            alert('No se encontraron resultados. Volviendo a la página principal...');
            window.location.href = '/';
            return;
        }
        
        console.log(`Recibidos ${results.length} resultados:`, results);
        
        // Guardar resultados globalmente para referencia futura
        window.allResults = results;
        
        // Mostrar los resultados en la página
        displayResults(results);
        
        // Configurar los botones de navegación
        setupNavigation(results);
        
        // Configurar el botón "Tomar otra foto"
        setupTakeAnotherPhotoButton();
        
        // Forzar la visibilidad de las flechas de nuevo después de un tiempo
        if (results.length > 1) {
            setTimeout(() => {
                const prevButton = document.querySelector('.flechai');
                const nextButton = document.querySelector('.flechad');
                
                if (prevButton) prevButton.setAttribute('style', 'display: block !important; z-index: 9999;');
                if (nextButton) nextButton.setAttribute('style', 'display: block !important; z-index: 9999;');
            }, 1000);
        }
        
    } catch (error) {
        console.error('Error al obtener los resultados:', error);
        alert('Error al cargar los resultados. Volviendo a la página principal...');
        window.location.href = '/';
    }
});

// Función para mostrar los resultados en la página
function displayResults(results) {
    try {
        console.log("Mostrando resultados:", results);
        
        // Verificar que results es un array y tiene elementos
        if (!Array.isArray(results) || results.length === 0) {
            console.error("Error: No hay resultados para mostrar");
            return;
        }
        
        // Obtener el resultado para el índice actual
        const currentIndex = window.currentPersonIndex || 0;
        
        // Verificar que el índice está dentro del rango
        if (currentIndex < 0 || currentIndex >= results.length) {
            console.error(`Error: Índice ${currentIndex} fuera de rango (0-${results.length-1})`);
            window.currentPersonIndex = 0; // Resetear al primer elemento
        }
        
        const currentResult = results[window.currentPersonIndex || 0];
        
        // Verificar que el resultado actual existe y tiene la propiedad cara_detectada
        if (!currentResult || !currentResult.cara_detectada) {
            console.error("Error: El resultado actual no tiene la propiedad cara_detectada", currentResult);
            return;
        }
        
        console.log(`Mostrando persona ${window.currentPersonIndex + 1} de ${results.length}:`, currentResult);
        
        // Mostrar la imagen detectada de la cara en el cuadrado pequeño (cuadrado4)
        const personaImg = document.createElement('img');
        personaImg.src = `/${currentResult.cara_detectada}`;
        personaImg.alt = 'Tu foto';
        personaImg.className = 'cara-detectada';
        
        // Obtener los cuadrados donde se mostrarán las imágenes
        const cuadrado1 = document.querySelector('.cuadrado1');
        const cuadrado2 = document.querySelector('.cuadrado2');
        const cuadrado3 = document.querySelector('.cuadrado3');
        const cuadrado4 = document.querySelector('.cuadrado4');
        
        // Verificar que los elementos existen
        if (!cuadrado1 || !cuadrado2 || !cuadrado3 || !cuadrado4) {
            console.error("Error: No se encontraron los elementos cuadrado");
            return;
        }
        
        // Limpiar los cuadrados
        cuadrado1.innerHTML = '';
        cuadrado2.innerHTML = '';
        cuadrado3.innerHTML = '';
        cuadrado4.innerHTML = '';
        
        // Mostrar la imagen de la cara detectada en el cuadrado pequeño (cuadrado4)
        cuadrado4.appendChild(personaImg);
        
        // Verificar que matches existe antes de intentar iterarlo
        if (currentResult.matches && Array.isArray(currentResult.matches) && currentResult.matches.length > 0) {
            // Mostrar los famosos en los cuadrados grandes
            for (let i = 0; i < Math.min(3, currentResult.matches.length); i++) {
                const match = currentResult.matches[i];
                // Verificar que el match es válido
                if (!match) continue;
                
                // Seleccionar el cuadrado correspondiente (1, 2 o 3)
                const cuadrado = i === 0 ? cuadrado1 : (i === 1 ? cuadrado2 : cuadrado3);
                
                // Crear la imagen del famoso
                const famousImg = document.createElement('img');
                
                // Verificar que image_data existe
                if (match.image_data) {
                    famousImg.src = `/${match.image_data}`;
                } else {
                    famousImg.src = '/Static/img/image-not-found.svg';
                }
                
                famousImg.alt = match.name || 'Celebridad';
                famousImg.className = 'famous-img';
                
                // Añadir un manejador de errores para la imagen
                famousImg.onerror = function() {
                    this.src = '/Static/img/image-not-found.svg';
                    this.alt = 'Imagen no encontrada';
                };
                
                // Crear el div para mostrar el nombre y el porcentaje
                const infoDiv = document.createElement('div');
                infoDiv.className = 'famous-info';
                infoDiv.innerHTML = `
                    <p class="famous-name">${match.name || 'Desconocido'}</p>
                    <p class="famous-similarity">${match.similarity || 0}% de similitud</p>
                `;
                
                // Añadir la imagen y la información al cuadrado
                cuadrado.appendChild(famousImg);
                cuadrado.appendChild(infoDiv);
            }
        } else {
            // Si no hay coincidencias, mostrar un mensaje en los tres cuadrados
            const noMatchesMessage = document.createElement('div');
            noMatchesMessage.className = 'famous-info';
            noMatchesMessage.innerHTML = '<p class="famous-name">No se encontraron coincidencias</p>';
            
            cuadrado1.appendChild(noMatchesMessage.cloneNode(true));
            cuadrado2.appendChild(noMatchesMessage.cloneNode(true));
            cuadrado3.appendChild(noMatchesMessage.cloneNode(true));
        }
        
        // Actualizar el contador de personas si hay más de una
        updatePersonCounter(results);
        
        // Asegurarse de que las flechas sean visibles si hay más de una persona
        if (results.length > 1) {
            console.log("Mostrando flechas para navegación entre personas");
            const prevButton = document.querySelector('.flechai');
            const nextButton = document.querySelector('.flechad');
            
            if (prevButton) prevButton.style.display = 'block';
            if (nextButton) nextButton.style.display = 'block';
        }
    } catch (error) {
        console.error("Error al mostrar resultados:", error);
    }
}

// Función para actualizar el contador de personas
function updatePersonCounter(results) {
    // Eliminar el contador existente si lo hay
    const existingCounter = document.getElementById('person-counter');
    if (existingCounter) {
        existingCounter.remove();
    }
    
    // Si hay más de una persona, mostrar el contador
    if (results.length > 1) {
        const currentIndex = window.currentPersonIndex || 0;
        
        // Crear el contador
        const counter = document.createElement('div');
        counter.id = 'person-counter';
        counter.className = 'person-counter';
        counter.innerHTML = `
            <span>Persona ${currentIndex + 1} de ${results.length}</span>
        `;
        
        // Añadir el contador a la página en una ubicación mejor (no en .enunciado)
        const container = document.querySelector('.main-content');
        if (container) {
            container.appendChild(counter);
        }
    }
}

// Función para configurar los botones de navegación
function setupNavigation(results) {
    try {
        // Guardar el índice actual en una variable global
        window.currentPersonIndex = 0;
        
        // Verificar que results es un array válido
        if (!Array.isArray(results)) {
            console.error("Error: results no es un array válido", results);
            return;
        }
        
        const totalPersons = results.length;
        console.log(`Configurando navegación para ${totalPersons} personas`);
        
        // Obtener los botones de navegación
        const prevButton = document.querySelector('.flechai');
        const nextButton = document.querySelector('.flechad');
        
        // Verificar que los elementos existen
        if (!prevButton || !nextButton) {
            console.error("Error: No se encontraron los botones de navegación");
            return;
        }
        
        // Ocultar los botones si solo hay una persona
        if (totalPersons <= 1) {
            prevButton.style.display = 'none';
            nextButton.style.display = 'none';
            return;
        }
        
        // Mostrar los botones si hay más de una persona
        prevButton.style.display = 'block';
        nextButton.style.display = 'block';
        
        // Configurar el botón anterior con mejor manejo de errores
        prevButton.onclick = function() {
            try {
                window.currentPersonIndex = (window.currentPersonIndex - 1 + totalPersons) % totalPersons;
                console.log(`Navegando a persona anterior: ${window.currentPersonIndex + 1} de ${totalPersons}`);
                displayResults(results);
            } catch (error) {
                console.error("Error al navegar a la persona anterior:", error);
            }
        };
        
        // Configurar el botón siguiente con mejor manejo de errores
        nextButton.onclick = function() {
            try {
                window.currentPersonIndex = (window.currentPersonIndex + 1) % totalPersons;
                console.log(`Navegando a persona siguiente: ${window.currentPersonIndex + 1} de ${totalPersons}`);
                displayResults(results);
            } catch (error) {
                console.error("Error al navegar a la persona siguiente:", error);
            }
        };
        
        // También permitir navegación con las teclas de flecha
        document.addEventListener('keydown', (event) => {
            if (event.key === 'ArrowLeft') {
                prevButton.click();
            } else if (event.key === 'ArrowRight') {
                nextButton.click();
            }
        });
    } catch (error) {
        console.error("Error al configurar la navegación:", error);
    }
}

// Función para configurar el botón "Tomar otra foto"
function setupTakeAnotherPhotoButton() {
    const takeAnotherButton = document.getElementById('take-another-photo');
    if (takeAnotherButton) {
        takeAnotherButton.addEventListener('click', async () => {
            try {
                // Mostrar un efecto visual al hacer clic
                takeAnotherButton.textContent = 'PROCESANDO...';
                takeAnotherButton.disabled = true;
                
                // Limpiar los datos actuales
                await fetch('/clear_data', {
                    method: 'POST',
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Datos limpiados:", data);
                    
                    // Redirigir a la página principal con un parámetro para forzar recarga
                    window.location.href = '/?reload=' + new Date().getTime();
                })
                .catch(error => {
                    console.error('Error al limpiar los datos:', error);
                    // En caso de error, redirigir igualmente
                    window.location.href = '/?reload=' + new Date().getTime();
                });
            } catch (error) {
                console.error('Error al limpiar los datos:', error);
                // En caso de error, redirigir igualmente
                window.location.href = '/?reload=' + new Date().getTime();
            }
        });
    }
}

// Función para volver a la página principal y limpiar los datos
document.addEventListener('keydown', async (event) => {
    // Si se presiona la tecla Escape, volver a la página principal
    if (event.key === 'Escape') {
        try {
            // Limpiar los datos
            await fetch('/clear_data', {
                method: 'POST',
            });
            
            // Volver a la página principal
            window.location.href = '/';
        } catch (error) {
            console.error('Error al limpiar los datos:', error);
            window.location.href = '/';
        }
    }
});
