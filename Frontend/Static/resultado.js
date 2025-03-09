var num_personas ; //El número de personas que aparecen el la fotografía
var n; //variable para el bucle for
let imagen ; //arreglo para las imágenes

// Script para mostrar los resultados en la página de resultados

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Obtener los resultados del servidor
        const response = await fetch('/get_results');
        const results = await response.json();
        
        if (!results || results.length === 0 || results.error) {
            console.error('No se encontraron resultados o hubo un error:', results.error);
            alert('No se encontraron resultados. Volviendo a la página principal...');
            window.location.href = '/';
            return;
        }
        
        // Mostrar los resultados en la página
        displayResults(results);
        
        // Configurar los botones de navegación
        setupNavigation(results);
        
        // Configurar el botón "Tomar otra foto"
        setupTakeAnotherPhotoButton();
        
    } catch (error) {
        console.error('Error al obtener los resultados:', error);
        alert('Error al cargar los resultados. Volviendo a la página principal...');
        window.location.href = '/';
    }
});

// Función para mostrar los resultados en la página
function displayResults(results) {
    // Obtener el primer resultado (primera persona)
    const firstResult = results[0];
    
    // Mostrar la imagen original de la persona en el cuadrado pequeño (cuadrado4)
    const personaImg = document.createElement('img');
    personaImg.src = `/${firstResult.persona}`;  // Siempre usar la imagen original (foto.jpg)
    personaImg.alt = 'Tu foto';
    personaImg.className = 'persona-img';
    
    // Obtener los cuadrados donde se mostrarán las imágenes
    const cuadrado1 = document.querySelector('.cuadrado1');
    const cuadrado2 = document.querySelector('.cuadrado2');
    const cuadrado3 = document.querySelector('.cuadrado3');
    const cuadrado4 = document.querySelector('.cuadrado4');
    
    // Limpiar los cuadrados
    cuadrado1.innerHTML = '';
    cuadrado2.innerHTML = '';
    cuadrado3.innerHTML = '';
    cuadrado4.innerHTML = '';
    
    // Mostrar la imagen original de la persona en el cuadrado pequeño (cuadrado4)
    cuadrado4.appendChild(personaImg);
    
    // Mostrar las imágenes de los famosos en los otros cuadrados
    if (firstResult.matches && firstResult.matches.length > 0) {
        // Mostrar los tres famosos en los cuadrados grandes
        for (let i = 0; i < Math.min(3, firstResult.matches.length); i++) {
            const match = firstResult.matches[i];
            // Seleccionar el cuadrado correspondiente (1, 2 o 3)
            const cuadrado = i === 0 ? cuadrado1 : (i === 1 ? cuadrado2 : cuadrado3);
            
            // Crear la imagen del famoso
            const famousImg = document.createElement('img');
            
            // Asegurarse de que la ruta de la imagen sea correcta
            const imagePath = match.image_data;
            famousImg.src = `/${imagePath}`;
            famousImg.alt = match.name;
            famousImg.className = 'famous-img';
            
            // Añadir un manejador de errores para la imagen
            famousImg.onerror = function() {
                console.error(`Error loading image: ${famousImg.src}`);
                // Mostrar un mensaje de error o una imagen de reemplazo
                this.src = '/Static/img/image-not-found.svg';
                this.alt = 'Imagen no encontrada';
            };
            
            // Crear el div para mostrar el nombre y el porcentaje
            const infoDiv = document.createElement('div');
            infoDiv.className = 'famous-info';
            infoDiv.innerHTML = `
                <p class="famous-name">${match.name}</p>
                <p class="famous-similarity">${match.similarity}% de similitud</p>
            `;
            
            // Añadir la imagen y la información al cuadrado
            cuadrado.appendChild(famousImg);
            cuadrado.appendChild(infoDiv);
        }
    }
    
    // Actualizar el contador de personas si hay más de una
    updatePersonCounter(results);
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
        
        // Añadir el contador a la página
        const container = document.querySelector('.enunciado');
        if (container) {
            container.appendChild(counter);
        }
    }
}

// Función para configurar los botones de navegación
function setupNavigation(results) {
    // Guardar el índice actual en una variable global
    window.currentPersonIndex = 0;
    const totalPersons = results.length;
    
    // Obtener los botones de navegación
    const prevButton = document.querySelector('.flechai');
    const nextButton = document.querySelector('.flechad');
    
    // Ocultar los botones si solo hay una persona
    if (totalPersons <= 1) {
        prevButton.style.display = 'none';
        nextButton.style.display = 'none';
        return;
    }
    
    // Mostrar los botones si hay más de una persona
    prevButton.style.display = 'block';
    nextButton.style.display = 'block';
    
    // Añadir títulos para mejorar la usabilidad
    prevButton.title = 'Persona anterior';
    nextButton.title = 'Persona siguiente';
    
    // Configurar el botón anterior
    prevButton.addEventListener('click', () => {
        window.currentPersonIndex = (window.currentPersonIndex - 1 + totalPersons) % totalPersons;
        
        // Crear un nuevo array con el resultado actual y mantener la imagen original
        const currentResult = JSON.parse(JSON.stringify(results[window.currentPersonIndex]));
        
        // Asegurarse de que siempre se use la imagen original (foto.jpg)
        currentResult.persona = "personas/foto.jpg";
        
        displayResults([currentResult]);
    });
    
    // Configurar el botón siguiente
    nextButton.addEventListener('click', () => {
        window.currentPersonIndex = (window.currentPersonIndex + 1) % totalPersons;
        
        // Crear un nuevo array con el resultado actual y mantener la imagen original
        const currentResult = JSON.parse(JSON.stringify(results[window.currentPersonIndex]));
        
        // Asegurarse de que siempre se use la imagen original (foto.jpg)
        currentResult.persona = "personas/foto.jpg";
        
        displayResults([currentResult]);
    });
    
    // También permitir navegación con las teclas de flecha
    document.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowLeft') {
            prevButton.click();
        } else if (event.key === 'ArrowRight') {
            nextButton.click();
        }
    });
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
                });
                
                // Redirigir a la página principal
                window.location.href = '/';
            } catch (error) {
                console.error('Error al limpiar los datos:', error);
                alert('Error al limpiar los datos. Inténtalo de nuevo.');
                takeAnotherButton.textContent = 'TOMAR OTRA FOTO';
                takeAnotherButton.disabled = false;
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
