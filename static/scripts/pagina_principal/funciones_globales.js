// Manejo de error de permisos y cuentas inactivas

window.handlePermissionError = function(data, defaultRedirect = '/login'){
    Swal.fire({
        title: 'Error',
        icon: 'error',
        text: data.message,
        confirmButtonText: 'Entendido'
    })
    .then(() =>{
        window.location.href = data.redirect_url || defaultRedirect;
    });
}

// ========================================
// FUNCIONES DE UTILIDAD
// ========================================

// Formatear precios en pesos colombianos
wiwndow.formatPrice = function(price) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(price);
}

// Validar email (para futuros formularios)
window.validateEmail = function (email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Función para cambiar tema (light/dark) - funcionalidad futura
window.toggleTheme = function () {
    document.body.classList.toggle('light-theme');
    // Guardar preferencia en localStorage sería ideal aquí
    // pero recordemos que localStorage no está disponible en artifacts
}