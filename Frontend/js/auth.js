/**
 * Файл для аутентификации пользователей
 * Обработка форм входа, регистрации и выхода
 */

// API URL
const API_BASE_URL = 'http://localhost:8000/api';

// Токен авторизации
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');

// DOM элементы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация GSAP анимаций
    initAnimations();
    
    // Проверка авторизации
    checkAuth();
    
    // Обработчики переключения видимости пароля
    setupPasswordToggles();
    
    // Форма входа
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Форма регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Кнопка выхода
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }
});

/**
 * Инициализация GSAP анимаций
 */
function initAnimations() {
    gsap.from('.login-card, .register-card', {
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: 'power3.out',
        stagger: 0.2
    });
    
    gsap.from('.welcome-section', {
        duration: 1,
        x: -30,
        opacity: 0,
        ease: 'power3.out',
        delay: 0.3
    });
}

/**
 * Настройка переключателей видимости пароля
 */
function setupPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Изменение иконки
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    });
}

/**
 * Проверка авторизации пользователя
 */
function checkAuth() {
    if (authToken) {
        // Пользователь авторизован
        document.querySelectorAll('.auth-buttons').forEach(el => {
            el.style.display = 'none';
        });
        
        document.querySelectorAll('.user-profile').forEach(el => {
            el.style.display = 'block';
        });
        
        // Обновление информации о пользователе
        document.querySelectorAll('#userName').forEach(el => {
            if (currentUser) {
                el.textContent = currentUser.username;
            }
        });
    } else {
        // Пользователь не авторизован
        document.querySelectorAll('.auth-buttons').forEach(el => {
            el.style.display = 'block';
        });
        
        document.querySelectorAll('.user-profile').forEach(el => {
            el.style.display = 'none';
        });
    }
}

/**
 * Обработчик входа в систему
 * @param {Event} event - Событие отправки формы
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginError = document.getElementById('loginError');
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Сохранение токена и информации о пользователе
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('currentUser', JSON.stringify({
                id: data.user_id,
                username: data.username,
                email: data.email
            }));
            
            // Перенаправление на профиль
            window.location.href = 'profile.html';
        } else {
            // Отображение ошибки
            loginError.textContent = data.detail || 'Ошибка при входе. Пожалуйста, попробуйте снова.';
            loginError.classList.remove('d-none');
            
            // Анимация ошибки
            gsap.fromTo(loginError, 
                { y: -20, opacity: 0 }, 
                { y: 0, opacity: 1, duration: 0.3 }
            );
        }
    } catch (error) {
        console.error('Ошибка при входе:', error);
        loginError.textContent = 'Ошибка сервера. Пожалуйста, попробуйте позже.';
        loginError.classList.remove('d-none');
    }
}

/**
 * Обработчик регистрации пользователя
 * @param {Event} event - Событие отправки формы
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const registerError = document.getElementById('registerError');
    
    // Проверка совпадения паролей
    if (password !== confirmPassword) {
        registerError.textContent = 'Пароли не совпадают';
        registerError.classList.remove('d-none');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Перенаправление на страницу входа с сообщением об успешной регистрации
            window.location.href = 'login.html?registered=true';
        } else {
            // Отображение ошибки
            registerError.textContent = data.detail || 'Ошибка при регистрации. Пожалуйста, попробуйте снова.';
            registerError.classList.remove('d-none');
            
            // Анимация ошибки
            gsap.fromTo(registerError, 
                { y: -20, opacity: 0 }, 
                { y: 0, opacity: 1, duration: 0.3 }
            );
        }
    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        registerError.textContent = 'Ошибка сервера. Пожалуйста, попробуйте позже.';
        registerError.classList.remove('d-none');
    }
}

/**
 * Обработчик выхода из системы
 * @param {Event} event - Событие клика
 */
function handleLogout(event) {
    event.preventDefault();
    
    // Удаление данных авторизации
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    // Перенаправление на главную страницу
    window.location.href = 'index.html';
}

/**
 * Получение данных текущего пользователя с сервера
 * @returns {Promise<Object>} - Данные пользователя
 */
async function fetchCurrentUser() {
    if (!authToken) return null;
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            return await response.json();
        } else if (response.status === 401) {
            // Если токен невалиден, выход из системы
            handleLogout({ preventDefault: () => {} });
        }
        return null;
    } catch (error) {
        console.error('Ошибка при получении данных пользователя:', error);
        return null;
    }
} 