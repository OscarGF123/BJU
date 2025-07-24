// Variables globales para el carrito
let cart = [];
let cartCount = 0;

// ========================================
// FUNCIONES DEL HEADER
// ========================================

// Cambiar estilo del header al hacer scroll
window.addEventListener('scroll', function() {
    const header = document.getElementById('header');
    if (window.scrollY > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Toggle del menú móvil
function toggleMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    navMenu.classList.toggle('active');
}

// ========================================
// FUNCIONES DE NAVEGACIÓN
// ========================================

// Scroll suave a la sección de productos
function scrollToProducts() {
    document.getElementById('productos').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// ========================================
// FUNCIONES DEL CARRITO DE COMPRAS
// ========================================

// Agregar producto al carrito
function addToCart(productName, price) {
    cart.push({
        name: productName,
        price: price
    });
    cartCount++;
    updateCartButton();
    
    // Animación de confirmación
    showNotification(`${productName} agregado al carrito!`);
}

// Actualizar el botón del carrito
function updateCartButton() {
    const cartBtn = document.querySelector('.cart-btn');
    cartBtn.textContent = `🛒 Carrito (${cartCount})`;
    
    // Animación del botón
    cartBtn.style.transform = 'scale(1.1)';
    setTimeout(() => {
        cartBtn.style.transform = 'scale(1)';
    }, 200);
}

// Mostrar carrito (función placeholder)
function showCart() {
    let cartMessage = 'Productos en el carrito:\n\n';
    let total = 0;
    
    if (cart.length === 0) {
        alert('Tu carrito está vacío');
        return;
    }
    
    cart.forEach(item => {
        cartMessage += `${item.name} - $${item.price.toLocaleString()}\n`;
        total += item.price;
    });
    
    cartMessage += `\nTotal: $${total.toLocaleString()}`;
    alert(cartMessage);
}

// ========================================
// SISTEMA DE NOTIFICACIONES
// ========================================

// Mostrar notificación
function showNotification(message) {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(45deg, #dc3545, #28a745);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        z-index: 10000;
        font-weight: bold;
        box-shadow: 0 8px 25px rgba(220, 53, 69, 0.4);
        transform: translateX(400px);
        transition: all 0.3s ease;
    `;
    notification.textContent = message;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ========================================
// ANIMACIONES DE SCROLL
// ========================================

// Observer para animaciones al hacer scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observar todos los elementos con clase 'fade-in'
document.addEventListener('DOMContentLoaded', function() {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        observer.observe(element);
    });
});

// ========================================
// EFECTOS ADICIONALES Y INTERACTIVIDAD
// ========================================

// Efecto parallax en el hero
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    const rate = scrolled * -0.5;
    
    if (hero) {
        hero.style.transform = `translateY(${rate}px)`;
    }
});

// Animación de hover en las tarjetas de productos
document.addEventListener('DOMContentLoaded', function() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Función para smooth scroll en los enlaces del nav
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId.startsWith('#')) {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
            
            // Cerrar menú móvil si está abierto
            const navMenu = document.getElementById('nav-menu');
            navMenu.classList.remove('active');
        });
    });
});

// Efecto de typing en el título del hero (opcional)
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Inicializar efectos cuando la página carga
window.addEventListener('load', function() {
    // Pequeño delay para que se vea el efecto
    setTimeout(() => {
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) {
            typeWriter(heroTitle, 'BOX JEANS URBAN', 150);
        }
    }, 500);
});

// ========================================
// FUNCIONES DE UTILIDAD
// ========================================

// Formatear precios en pesos colombianos
function formatPrice(price) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(price);
}

// Validar email (para futuros formularios)
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Función para cambiar tema (light/dark) - funcionalidad futura
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    // Guardar preferencia en localStorage sería ideal aquí
    // pero recordemos que localStorage no está disponible en artifacts
}

console.log('🎉 Box Jeans Urban - Sitio web cargado correctamente!');
console.log('📱 Responsive design activado');
console.log('🛒 Sistema de carrito funcional');
console.log('✨ Animaciones y efectos activos');

// ========================================
// JAVASCRIPT - FIN
// ========================================