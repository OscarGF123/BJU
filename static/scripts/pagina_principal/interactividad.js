// ========================================
// BOX JEANS URBAN - JAVASCRIPT (SIN CONFLICTOS)
// Namespace: BJU (Box Jeans Urban)
// ========================================

// Crear namespace para evitar conflictos
window.BJU = window.BJU || {};

// Variables globales para el carrito (dentro del namespace)
BJU.cart = [];
BJU.cartCount = 0;

// ========================================
// FUNCIONES DEL HEADER
// ========================================

// Cambiar estilo del header al hacer scroll
BJU.handleScroll = function() {
    const header = document.querySelector('.bju-header');
    if (header) {
        if (window.scrollY > 100) {
            header.classList.add('bju-scrolled');
        } else {
            header.classList.remove('bju-scrolled');
        }
    }
};

// Toggle del menú móvil
BJU.toggleMobileMenu = function() {
    const navMenu = document.querySelector('.bju-nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('bju-active');
    }
};

// Función global para compatibilidad con HTML existente
window.toggleMobileMenu = BJU.toggleMobileMenu;

// ========================================
// FUNCIONES DE NAVEGACIÓN
// ========================================

// Scroll suave a la sección de productos
BJU.scrollToProducts = function() {
    const productSection = document.getElementById('productos') || 
                          document.querySelector('.bju-products-section');
    if (productSection) {
        productSection.scrollIntoView({ 
            behavior: 'smooth' 
        });
    }
};

// Función global para compatibilidad con HTML existente
window.scrollToProducts = BJU.scrollToProducts;

// ========================================
// FUNCIONES DEL CARRITO DE COMPRAS
// ========================================

// Agregar producto al carrito
BJU.addToCart = function(productName, price) {
    BJU.cart.push({
        name: productName,
        price: price,
        id: Date.now() + Math.random() // ID único
    });
    BJU.cartCount++;
    BJU.updateCartButton();
    
    // Animación de confirmación
    BJU.showNotification(`${productName} agregado al carrito!`);
};

// Función global para compatibilidad con HTML existente
window.addToCart = BJU.addToCart;

// Actualizar el botón del carrito
BJU.updateCartButton = function() {
    const cartBtn = document.querySelector('.bju-cart-btn');
    if (cartBtn) {
        cartBtn.textContent = `🛒 Carrito (${BJU.cartCount})`;
        
        // Animación del botón
        cartBtn.style.transform = 'scale(1.1)';
        setTimeout(() => {
            cartBtn.style.transform = 'scale(1)';
        }, 200);
    }
};

// Mostrar carrito
BJU.showCart = function() {
    let cartMessage = 'Productos en el carrito:\n\n';
    let total = 0;
    
    if (BJU.cart.length === 0) {
        // Usar SweetAlert si está disponible, sino alert nativo
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Carrito vacío',
                text: 'Tu carrito está vacío',
                icon: 'info',
                confirmButtonColor: '#dc3545'
            });
        } else {
            alert('Tu carrito está vacío');
        }
        return;
    }
    
    BJU.cart.forEach(item => {
        cartMessage += `${item.name} - $${item.price.toLocaleString()}\n`;
        total += item.price;
    });
    
    cartMessage += `\nTotal: $${total.toLocaleString()}`;
    
    // Usar SweetAlert si está disponible, sino alert nativo
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Tu Carrito',
            text: cartMessage,
            icon: 'success',
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Continuar comprando'
        });
    } else {
        alert(cartMessage);
    }
};

// Función global para compatibilidad con HTML existente
window.showCart = BJU.showCart;

// ========================================
// SISTEMA DE NOTIFICACIONES
// ========================================

// Mostrar notificación
BJU.showNotification = function(message, type = 'success') {
    // Si SweetAlert está disponible, usarlo
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });

        Toast.fire({
            icon: type,
            title: message,
            background: '#2d2d2d',
            color: '#fff'
        });
        return;
    }

    // Fallback: crear notificación personalizada
    const notification = document.createElement('div');
    notification.className = 'bju-notification';
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
        font-family: "Poppins", sans-serif;;
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
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
};

// ========================================
// ANIMACIONES DE SCROLL
// ========================================

// Observer para animaciones al hacer scroll
BJU.createScrollObserver = function() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('bju-visible');
            }
        });
    }, observerOptions);

    return observer;
};

// Inicializar observer para elementos con animaciones
BJU.initScrollAnimations = function() {
    const observer = BJU.createScrollObserver();
    
    // Observar elementos con clases de animación
    const animatedElements = document.querySelectorAll(
        '.bju-fade-in, .bju-slide-in-left, .bju-slide-in-right, .bju-scale-in, .fade-in'
    );
    
    animatedElements.forEach(element => {
        // Agregar clase BJU si no la tiene
        if (!element.classList.contains('bju-fade-in') && 
            !element.classList.contains('bju-slide-in-left') && 
            !element.classList.contains('bju-slide-in-right') && 
            !element.classList.contains('bju-scale-in')) {
            element.classList.add('bju-fade-in');
        }
        observer.observe(element);
    });
};

// ========================================
// EFECTOS ADICIONALES Y INTERACTIVIDAD
// ========================================

// Efecto parallax en el hero
BJU.handleParallax = function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.bju-hero') || document.querySelector('.hero');
    
    if (hero) {
        const rate = scrolled * -0.5;
        hero.style.transform = `translateY(${rate}px)`;
    }
};

// Animación de hover en las tarjetas de productos
BJU.initProductCardHovers = function() {
    const productCards = document.querySelectorAll('.bju-product-card, .product-card');
    
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
};

// Función para smooth scroll en los enlaces del nav
BJU.initSmoothScroll = function() {
    const navLinks = document.querySelectorAll('.bju-nav-link, .nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const targetElement = document.querySelector(href);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
                
                // Cerrar menú móvil si está abierto
                const navMenu = document.querySelector('.bju-nav-menu, #nav-menu');
                if (navMenu) {
                    navMenu.classList.remove('bju-active', 'active');
                }
            }
        });
    });
};

// Efecto de typing en el título del hero
BJU.typeWriter = function(element, text, speed = 100) {
    if (!element) return;
    
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
};


// ========================================
// FUNCIONES DE UTILIDAD
// ========================================

// Formatear precios en pesos colombianos
BJU.formatPrice = function(price) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(price);
};

// Validar email
BJU.validateEmail = function(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

// Función para cambiar tema (light/dark)
BJU.toggleTheme = function() {
    document.body.classList.toggle('bju-light-theme');
    
    // Guardar preferencia usando una variable en memoria
    BJU.currentTheme = document.body.classList.contains('bju-light-theme') ? 'light' : 'dark';
};

// Función para detectar conflictos con otras librerías
BJU.detectConflicts = function() {
    const conflicts = [];
    
    // Verificar Bootstrap
    if (typeof bootstrap !== 'undefined' || typeof $().modal !== 'undefined') {
        conflicts.push('Bootstrap detectado');
    }
    
    // Verificar SweetAlert
    if (typeof Swal !== 'undefined') {
        conflicts.push('SweetAlert2 detectado');
    }
    
    // Verificar jQuery
    if (typeof $ !== 'undefined') {
        conflicts.push('jQuery detectado');
    }
    
    if (conflicts.length > 0) {
        console.log('🔍 BJU: Librerías detectadas:', conflicts.join(', '));
        console.log('✅ BJU: Modo compatibilidad activado');
    }
};

// ========================================
// MANEJO DE EVENTOS GLOBALES
// ========================================

// Event listeners principales
BJU.initEventListeners = function() {
    // Scroll events
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        BJU.handleScroll();
        
        // Throttle parallax para mejor rendimiento
        if (!scrollTimeout) {
            scrollTimeout = setTimeout(function() {
                BJU.handleParallax();
                scrollTimeout = null;
            }, 16); // ~60fps
        }
    });

    // Resize events
    window.addEventListener('resize', function() {
        // Reajustar elementos si es necesario
        BJU.handleResize();
    });

    // Click events para cerrar menú móvil al hacer click fuera
    document.addEventListener('click', function(e) {
        const navMenu = document.querySelector('.bju-nav-menu');
        const menuBtn = document.querySelector('.bju-mobile-menu-btn');
        
        if (navMenu && menuBtn && 
            !navMenu.contains(e.target) && 
            !menuBtn.contains(e.target)) {
            navMenu.classList.remove('bju-active');
        }
    });
};

// Manejar redimensionamiento de ventana
BJU.handleResize = function() {
    // Cerrar menú móvil si se cambia a desktop
    if (window.innerWidth > 768) {
        const navMenu = document.querySelector('.bju-nav-menu');
        if (navMenu) {
            navMenu.classList.remove('bju-active');
        }
    }
};

// ========================================
// INICIALIZACIÓN PRINCIPAL
// ========================================

// Inicializar cuando el DOM esté listo
BJU.init = function() {
    // Detectar conflictos con otras librerías
    BJU.detectConflicts();
    
    // Inicializar componentes
    BJU.initEventListeners();
    BJU.initScrollAnimations();
    BJU.initProductCardHovers();
    BJU.initSmoothScroll();
    
    // Efecto de typing en el título (con delay)
    setTimeout(() => {
        const heroTitle = document.querySelector('.bju-hero-title, .hero-title');
        if (heroTitle) {
            BJU.typeWriter(heroTitle, 'BOX JEANS URBAN', 150);
        }
    }, 500);
    

    
    console.log('🎉 Box Jeans Urban - Sitio web cargado correctamente!');
    console.log('📱 Responsive design activado');
    console.log('🛒 Sistema de carrito funcional');
    console.log('✨ Animaciones y efectos activos');
    console.log('🔒 Modo sin conflictos activado');
};

// Inicializar cuando el DOM esté completamente cargado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', BJU.init);
} else {
    BJU.init();
}

// También inicializar en window.load para asegurar que todo esté listo
window.addEventListener('load', function() {
    // Pequeñas inicializaciones adicionales que requieren que todo esté cargado
    setTimeout(() => {
        // Verificar si hay elementos que necesiten inicialización tardía
        const lateInitElements = document.querySelectorAll('[data-bju-late-init]');
        lateInitElements.forEach(element => {
            // Inicializar elementos que requieren carga completa
            element.classList.add('bju-ready');
        });
    }, 100);
});

// ========================================
// FUNCIONES GLOBALES PARA COMPATIBILIDAD
// ========================================

// Mantener funciones globales para compatibilidad con HTML existente
window.BJU = BJU;

// Funciones específicas para compatibilidad
if (typeof window.toggleMobileMenu === 'undefined') {
    window.toggleMobileMenu = BJU.toggleMobileMenu;
}
if (typeof window.scrollToProducts === 'undefined') {
    window.scrollToProducts = BJU.scrollToProducts;
}
if (typeof window.addToCart === 'undefined') {
    window.addToCart = BJU.addToCart;
}
if (typeof window.showCart === 'undefined') {
    window.showCart = BJU.showCart;
}

// ========================================
// JAVASCRIPT - FIN
// ========================================