// JavaScript adicional para mejorar la experiencia del usuario
document.addEventListener('DOMContentLoaded', function() {
    // Agregar efectos de sonido sutiles (opcional)
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
        });
    });

    document.getElementById("bjBtnCerrar").addEventListener('click', (e) =>{
        e.preventDefault();
        
    });
    
    // // Agregar funcionalidad a los botones de acción
    // document.addEventListener('click', function(e) {
        
    //     if (e.target.classList.contains('bj-btn-primary')) {
    //         // Simular acción exitosa
    //         console.log('Acción primaria ejecutada');
    //     }
        
    //     if (e.target.classList.contains('bj-btn-danger')) {
    //         // Simular acción de eliminación
    //         console.log('Acción de eliminación ejecutada');
    //         // Cerrar modal después de la acción
    //         const modal = e.target.closest('.modal');
    //         if (modal) {
    //             const bsModal = bootstrap.Modal.getInstance(modal);
    //             if (bsModal) {
    //                 bsModal.hide();
    //             }
    //         }
    //     }
    // });
    
    // Mejorar accesibilidad (cerrar modal con escape)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const bsModal = bootstrap.Modal.getInstance(openModal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
        }
    });
});