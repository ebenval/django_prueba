/**
 * Funciones JavaScript principales del proyecto.
 */

console.log('Script main.js cargado correctamente');

// Ejemplo: función para mostrar alertas personalizadas
function showAlert(message, type = 'info') {
    const alertBox = document.createElement('div');
    alertBox.textContent = message;
    alertBox.style.padding = '1rem';
    alertBox.style.marginBottom = '1rem';
    alertBox.style.borderRadius = '4px';

    if (type === 'success') {
        alertBox.style.backgroundColor = '#27ae60';
        alertBox.style.color = 'white';
    } else if (type === 'error') {
        alertBox.style.backgroundColor = '#e74c3c';
        alertBox.style.color = 'white';
    } else {
        alertBox.style.backgroundColor = '#3498db';
        alertBox.style.color = 'white';
    }

    document.body.insertBefore(alertBox, document.body.firstChild);

    // Remover alerta después de 3 segundos
    setTimeout(() => alertBox.remove(), 3000);
}

// Ejemplo de uso cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM está listo');
    
});
