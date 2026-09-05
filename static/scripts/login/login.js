
// ========================================
// VARIABLES GLOBALES
// ========================================

//csrf_token

function getCookie(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    // Does this cookie string begin with the name we want?
    if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
    }
    }
}
return cookieValue;
}

let currentSlide = 0;
const totalSlides = 4;
let slideInterval;
let touchStartX = 0;
let touchEndX = 0;

let scriptLogin = document.getElementById("scriptLogin");
const urlLogin = scriptLogin.dataset.urllogin;

// ========================================
// LOGIN
// ========================================

document.getElementById("loginForm").addEventListener('submit', function(e) {
    e.preventDefault();
    fetch(urlLogin, {
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
        method: "POST",
        body: new FormData(this)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success"){
            window.location.href = data.redirect_url
        } else if (data.status == 'error' && data.type == 'credentials_invalid') {
            Swal.fire({
                title: '¡Error!',
                html: `<p>Ocurrio un error al iniciar sesión:</p><p>${data.errors}</p>`,
                icon: 'error',
            });
        } else if(data.status === 'error' && data.type === 'inactive_account'){
                Swal.fire({
                    title: '¡Error!',
                    html: `</p>${data.errors}</p><p>Haz click <a href="${data.verification_link}">aqui</a> para verificar tu cuenta</p>`,
                    icon: 'error',
                });
        } else if (data.status === 'error' && data.typem === 'form_invalid'){

            let errorMessage = '<ul>';
            for (const [field, messages] of Object.entries(data.errors)) {
                errorMessage += `<li><strong>Campo ${field}:</strong> ${messages.join(', ')}</li>`;
            }
            errorMessage += '</ul>';

            Swal.fire({
                title: '¡Error!',
                text: `Ocurrio un error al iniciar sesión:\n${errorMessage}`,
                icon: 'error',
            });

        }
    })
    .catch(error => {
        Swal.fire({
            title: '¡Error!',
            icon: 'error',
            text: `Ocurrio un error inesperado, contacta con soporte ${error}`,
        });
    });
});
// ========================================
// FUNCIONES DEL CARRUSEL
// ========================================

function goToSlide(index) {
    // Remover clase active del slide actual
    document.querySelectorAll('.carousel-slide')[currentSlide].classList.remove('active');
    document.querySelectorAll('.indicator')[currentSlide].classList.remove('active');
    
    // Actualizar índice
    currentSlide = index;
    
    // Agregar clase active al nuevo slide
    document.querySelectorAll('.carousel-slide')[currentSlide].classList.add('active');
    document.querySelectorAll('.indicator')[currentSlide].classList.add('active');
}

function nextSlide() {
    const nextIndex = (currentSlide + 1) % totalSlides;
    goToSlide(nextIndex);
}

function prevSlide() {
    const prevIndex = currentSlide === 0 ? totalSlides - 1 : currentSlide - 1;
    goToSlide(prevIndex);
}

function startCarousel() {
    slideInterval = setInterval(nextSlide, 5000); // Cambiar cada 5 segundos
}

function stopCarousel() {
    clearInterval(slideInterval);
}

// ========================================
// GESTOS TÁCTILES PARA CARRUSEL
// ========================================

function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
}

function handleTouchMove(e) {
    // Prevenir scroll vertical mientras se desliza horizontalmente
    if (Math.abs(e.touches[0].clientX - touchStartX) > 50) {
        e.preventDefault();
    }
}

function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].clientX;
    handleSwipe();
}

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchEndX - touchStartX;
    
    if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
            // Swipe derecha - slide anterior
            prevSlide();
        } else {
            // Swipe izquierda - slide siguiente
            nextSlide();
        }
        
        // Reiniciar carrusel automático
        stopCarousel();
        setTimeout(startCarousel, 3000);
    }
}



// ========================================
// FUNCIONES DE UTILIDAD
// ========================================

function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.password-toggle');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = '👁️';
    }
}


function socialLogin(provider) {
    showNotification(`Iniciando sesión con ${provider}...`, 'info');
    
    // Aquí implementarías la lógica de OAuth
    setTimeout(() => {
        showNotification(`Login con ${provider} no disponible en demo`, 'warning');
    }, 1500);
}

function goToRegister() {
    showNotification('Redirigiendo a registro...', 'info');
    // window.location.href = '/register';
}

// ========================================
// SISTEMA DE NOTIFICACIONES MÓVIL
// ========================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    
    const colors = {
        success: 'linear-gradient(45deg, #28a745, #20c997)',
        error: 'linear-gradient(45deg, #dc3545, #fd7e14)',
        info: 'linear-gradient(45deg, #17a2b8, #6f42c1)',
        warning: 'linear-gradient(45deg, #ffc107, #fd7e14)'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%) translateY(-100px);
        background: ${colors[type] || colors.info};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        z-index: 10000;
        font-weight: bold;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        max-width: calc(100vw - 2rem);
        text-align: center;
        font-size: 0.9rem;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(-50%) translateY(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(-50%) translateY(-100px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ========================================
// INICIALIZACIÓN Y EVENT LISTENERS
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Configurar eventos táctiles para el carrusel
    const carouselSection = document.getElementById('carousel-section');
    carouselSection.addEventListener('touchstart', handleTouchStart, { passive: true });
    carouselSection.addEventListener('touchmove', handleTouchMove, { passive: false });
    carouselSection.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    // Efectos en inputs
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Iniciar carrusel automático
    startCarousel();
    
    // Pausar carrusel al interactuar con la sección
    carouselSection.addEventListener('touchstart', stopCarousel, {passive: true});
    carouselSection.addEventListener('mouseenter', stopCarousel);
    carouselSection.addEventListener('mouseleave', startCarousel);
});


// Soporte para teclado
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowLeft') {
        prevSlide();
        stopCarousel();
        setTimeout(startCarousel, 3000);
    } else if (e.key === 'ArrowRight') {
        nextSlide();
        stopCarousel();
        setTimeout(startCarousel, 3000);
    }
});

// Prevenir zoom en iOS en inputs
document.addEventListener('touchstart', function(e) {
    if (e.touches.length > 1) {
        e.preventDefault();
    }
}, { passive: false });

