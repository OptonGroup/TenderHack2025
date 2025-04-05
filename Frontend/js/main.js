/**
 * Основной JavaScript файл
 * Общие функции и инициализация элементов интерфейса
 */

// DOM элементы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок Bootstrap
    initTooltips();
    
    // Инициализация GSAP анимаций
    initAnimations();
    
    // Проверка URL параметров (для отображения сообщений)
    checkUrlParams();
    
    // Инициализация обработчиков событий
    setupEventHandlers();
});

/**
 * Инициализация всплывающих подсказок Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Инициализация GSAP анимаций
 */
function initAnimations() {
    // Анимация заголовка на главной странице
    const welcomeSection = document.querySelector('.welcome-section');
    if (welcomeSection) {
        gsap.from('.welcome-section h1', {
            duration: 1,
            y: -30,
            opacity: 0,
            ease: 'power3.out'
        });
        
        gsap.from('.welcome-section p', {
            duration: 1,
            y: -20,
            opacity: 0,
            ease: 'power3.out',
            delay: 0.3
        });
        
        gsap.from('.welcome-section .btn', {
            duration: 0.8,
            y: 20,
            opacity: 0,
            ease: 'power3.out',
            delay: 0.6,
            stagger: 0.2
        });
    }
}

/**
 * Проверка URL параметров
 */
function checkUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Проверка параметра успешной регистрации
    if (urlParams.get('registered') === 'true') {
        showSuccess('Регистрация прошла успешно! Теперь вы можете войти в систему.');
    }
}

/**
 * Настройка обработчиков событий
 */
function setupEventHandlers() {
    // Добавление плавной прокрутки для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Обработчик для кнопки "Наверх"
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * Отображение сообщения об успешном действии
 * @param {string} message - Текст сообщения
 */
function showSuccess(message) {
    // Создание элемента уведомления
    const alert = document.createElement('div');
    alert.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3 animate-fade-in';
    alert.style.zIndex = '9999';
    alert.textContent = message;
    
    // Добавление элемента на страницу
    document.body.appendChild(alert);
    
    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        gsap.to(alert, {
            opacity: 0,
            y: -20,
            duration: 0.5,
            onComplete: () => alert.remove()
        });
    }, 3000);
}

/**
 * Отображение сообщения об ошибке
 * @param {string} message - Текст сообщения
 */
function showError(message) {
    // Создание элемента уведомления
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger position-fixed top-0 start-50 translate-middle-x mt-3 animate-fade-in';
    alert.style.zIndex = '9999';
    alert.textContent = message;
    
    // Добавление элемента на страницу
    document.body.appendChild(alert);
    
    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        gsap.to(alert, {
            opacity: 0,
            y: -20,
            duration: 0.5,
            onComplete: () => alert.remove()
        });
    }, 3000);
}

/**
 * Форматирование даты в читаемый формат
 * @param {string} dateStr - Строка с датой в формате ISO
 * @returns {string} - Форматированная дата
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Форматирование валюты
 * @param {number} value - Числовое значение
 * @returns {string} - Форматированная строка суммы с валютой
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2
    }).format(value);
} 