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
        // Добавляем валидацию пароля при вводе
        const passwordField = document.getElementById('password');
        if (passwordField) {
            passwordField.addEventListener('input', validatePassword);
        }
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
    // Анимация появления форм
    const loginCard = document.querySelector('.login-card');
    const registerCard = document.querySelector('.register-card');
    
    if (loginCard) {
        gsap.fromTo(loginCard, 
            { opacity: 0, y: 20 }, 
            { opacity: 1, y: 0, duration: 0.5, clearProps: "all", 
              onComplete: function() {
                  // Явно устанавливаем непрозрачность после анимации
                  loginCard.style.opacity = 1;
                  loginCard.classList.add('gsap-fade-in');
              } 
            }
        );
    }
    
    if (registerCard) {
        gsap.fromTo(registerCard, 
            { opacity: 0, y: 20 }, 
            { opacity: 1, y: 0, duration: 0.5, clearProps: "all", 
              onComplete: function() {
                  // Явно устанавливаем непрозрачность после анимации
                  registerCard.style.opacity = 1;
                  registerCard.classList.add('gsap-fade-in');
              }
            }
        );
    }
}

/**
 * Проверка авторизации пользователя
 */
function checkAuth() {
    const userProfile = document.querySelector('.user-profile');
    const authButtons = document.querySelector('.auth-buttons');
    
    if (authToken && currentUser) {
        // Пользователь авторизован
        if (userProfile) {
            userProfile.classList.remove('d-none');
        }
        if (authButtons) {
            authButtons.classList.add('d-none');
        }
        
        // Заполняем информацию о пользователе
        const userName = document.getElementById('userName');
        const profileUserName = document.getElementById('profileUserName');
        
        if (userName) {
            userName.textContent = currentUser.username;
        }
        
        if (profileUserName) {
            profileUserName.textContent = currentUser.username;
        }
    } else {
        // Пользователь не авторизован
        if (userProfile) {
            userProfile.classList.add('d-none');
        }
        if (authButtons) {
            authButtons.classList.remove('d-none');
        }
    }
}

/**
 * Настройка переключателей видимости пароля
 */
function setupPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const inputField = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (inputField.type === 'password') {
                inputField.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                inputField.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
}

/**
 * Валидация пароля
 */
function validatePassword() {
    const password = document.getElementById('password').value;
    const passwordFeedback = document.getElementById('passwordFeedback');
    
    if (!passwordFeedback) {
        return;
    }
    
    // Критерии сложности пароля
    const minLength = 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasDigit = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
    
    // Проверяем каждый критерий
    let errors = [];
    
    if (password.length < minLength) {
        errors.push(`Минимальная длина пароля - ${minLength} символов`);
    }
    
    if (!hasUppercase) {
        errors.push('Пароль должен содержать хотя бы одну заглавную букву');
    }
    
    if (!hasLowercase) {
        errors.push('Пароль должен содержать хотя бы одну строчную букву');
    }
    
    if (!hasDigit) {
        errors.push('Пароль должен содержать хотя бы одну цифру');
    }
    
    if (!hasSpecial) {
        errors.push('Пароль должен содержать хотя бы один специальный символ');
    }
    
    // Выводим результат проверки
    if (errors.length > 0) {
        passwordFeedback.innerHTML = '<ul class="mb-0">' + errors.map(error => `<li>${error}</li>`).join('') + '</ul>';
        passwordFeedback.classList.remove('d-none');
        passwordFeedback.classList.remove('text-success');
        passwordFeedback.classList.add('text-danger');
        return false;
    } else {
        passwordFeedback.innerHTML = 'Пароль соответствует требованиям безопасности';
        passwordFeedback.classList.remove('d-none');
        passwordFeedback.classList.remove('text-danger');
        passwordFeedback.classList.add('text-success');
        return true;
    }
}

/**
 * Обработчик входа пользователя
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
            // Сохраняем токен и данные пользователя
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('currentUser', JSON.stringify({
                id: data.user_id,
                username: data.username,
                email: data.email
            }));
            
            // Перенаправляем на профиль или главную страницу
            window.location.href = '/profile';
        } else {
            // Отображаем ошибку
            if (loginError) {
                loginError.classList.remove('d-none');
                gsap.fromTo(loginError, 
                    { y: -20, opacity: 0 }, 
                    { y: 0, opacity: 1, duration: 0.3 }
                );
            }
        }
    } catch (error) {
        console.error('Ошибка при входе:', error);
        if (loginError) {
            loginError.textContent = 'Ошибка сервера. Пожалуйста, попробуйте позже.';
            loginError.classList.remove('d-none');
        }
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
    
    // Валидация пароля
    if (!validatePassword()) {
        return;
    }
    
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
            window.location.href = '/login?registered=true';
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
 * Обработчик выхода пользователя
 * @param {Event} event - Событие клика
 */
function handleLogout(event) {
    event.preventDefault();
    
    // Удаляем данные авторизации
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    // Перенаправляем на главную страницу
    window.location.href = '/';
}
