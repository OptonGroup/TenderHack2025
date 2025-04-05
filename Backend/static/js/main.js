/**
 * Основной скрипт для веб-сайта Портала Поставщиков
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок (tooltips)
    initializeTooltips();
    
    // Инициализация анимаций
    initializeAnimations();
    
    // Обработчики для мобильного меню
    setupMobileMenu();
    
    // Обработчик смены языка
    setupLanguageSelector();
});

/**
 * Инициализация всплывающих подсказок Bootstrap
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Инициализация GSAP анимаций для элементов сайта
 */
function initializeAnimations() {
    // Анимация заголовка на главной странице
    const welcomeTitle = document.querySelector('.welcome-title');
    if (welcomeTitle) {
        gsap.from(welcomeTitle, {
            duration: 1,
            y: 30,
            opacity: 0,
            ease: 'power3.out'
        });
    }
    
    // Анимация карточек на главной странице
    const cards = document.querySelectorAll('.card');
    if (cards.length > 0) {
        gsap.from(cards, {
            duration: 0.8,
            opacity: 0,
            y: 20,
            stagger: 0.2,
            ease: 'power2.out',
            delay: 0.3
        });
    }
    
    // Анимация навигационных элементов
    const navItems = document.querySelectorAll('.nav-item');
    if (navItems.length > 0) {
        gsap.from(navItems, {
            duration: 0.5,
            opacity: 0,
            x: -10,
            stagger: 0.1,
            ease: 'power1.out'
        });
    }
}

/**
 * Настройка обработчиков для мобильного меню
 */
function setupMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Добавляем плавное закрытие меню при клике на пункт меню
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Проверяем, открыто ли меню и видим ли переключатель (т.е. находимся на малом экране)
                if (navbarCollapse.classList.contains('show') && window.getComputedStyle(navbarToggler).display !== 'none') {
                    navbarToggler.click();
                }
            });
        });
    }
}

/**
 * Настройка селектора языка
 */
function setupLanguageSelector() {
    const languageItems = document.querySelectorAll('.dropdown-item[lang]');
    
    languageItems.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            
            const language = this.getAttribute('lang');
            
            // Здесь можно добавить логику смены языка
            console.log(`Switching language to: ${language}`);
            
            // Временное решение: просто обновляем страницу
            // В реальном приложении здесь нужно отправить запрос на смену языка
            // или использовать библиотеку для интернационализации
            // window.location.reload();
        });
    });
}

/**
 * Функция для показа уведомлений
 * @param {string} message - текст уведомления
 * @param {string} type - тип уведомления (success, danger, warning, info)
 * @param {number} duration - длительность отображения в миллисекундах
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                          type === 'danger' ? 'fa-times-circle' : 
                          type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
        </div>
        <div class="notification-content">${message}</div>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Добавляем в контейнер уведомлений или создаем его
    let notificationsContainer = document.querySelector('.notifications-container');
    if (!notificationsContainer) {
        notificationsContainer = document.createElement('div');
        notificationsContainer.className = 'notifications-container';
        document.body.appendChild(notificationsContainer);
    }
    
    notificationsContainer.appendChild(notification);
    
    // Анимируем появление
    gsap.fromTo(notification, 
        { opacity: 0, x: 50 }, 
        { opacity: 1, x: 0, duration: 0.3 }
    );
    
    // Устанавливаем автоматическое закрытие
    const timer = setTimeout(() => closeNotification(notification), duration);
    
    // Обработчик закрытия по кнопке
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        clearTimeout(timer);
        closeNotification(notification);
    });
}

/**
 * Закрытие уведомления с анимацией
 * @param {HTMLElement} notification - элемент уведомления
 */
function closeNotification(notification) {
    gsap.to(notification, { 
        opacity: 0, 
        x: 50, 
        duration: 0.3,
        onComplete: () => notification.remove() 
    });
} 