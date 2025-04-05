/**
 * Скрипт для управления аутентификацией и авторизацией
 */

document.addEventListener('DOMContentLoaded', function() {
    // Проверяем наличие токена аутентификации в localStorage
    const token = localStorage.getItem('token');
    
    if (token) {
        // Если токен есть, скрываем кнопки авторизации и показываем профиль
        toggleAuthButtons(false);
        updateUserProfile();
    } else {
        // Если токена нет, показываем кнопки авторизации и скрываем профиль
        toggleAuthButtons(true);
    }
    
    // Обработка формы логина
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Обработка формы регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        
        // Проверка надежности пароля
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', validatePassword);
        }
        
        // Проверка совпадения паролей
        const confirmPasswordInput = document.getElementById('confirmPassword');
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', validatePasswordMatch);
        }
    }
    
    // Обработка кнопки выхода
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }
    
    // Кнопки для отображения/скрытия пароля
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', togglePasswordVisibility);
    });
});

/**
 * Переключение отображения кнопок авторизации и профиля пользователя
 * @param {boolean} showAuthButtons - флаг, показывать ли кнопки авторизации
 */
function toggleAuthButtons(showAuthButtons) {
    const authButtons = document.querySelector('.auth-buttons');
    const userProfile = document.querySelector('.user-profile');
    
    if (authButtons && userProfile) {
        if (showAuthButtons) {
            authButtons.classList.remove('d-none');
            userProfile.classList.add('d-none');
        } else {
            authButtons.classList.add('d-none');
            userProfile.classList.remove('d-none');
        }
    }
}

/**
 * Обновление данных профиля пользователя
 */
async function updateUserProfile() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch('/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            
            // Обновляем имя пользователя
            const userName = document.getElementById('userName');
            if (userName) {
                userName.textContent = userData.username;
            }
            
            // Обновляем другие данные профиля, если они есть
            // ...
        } else {
            // Если запрос неудачен, удаляем токен и перенаправляем на страницу входа
            localStorage.removeItem('token');
            toggleAuthButtons(true);
        }
    } catch (error) {
        console.error('Ошибка при получении данных пользователя:', error);
    }
}

/**
 * Обработка формы входа
 * @param {Event} event - событие отправки формы
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe')?.checked;
    
    try {
        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Сохраняем токен в localStorage
            localStorage.setItem('token', data.access_token);
            
            // Если пользователь на странице логина, перенаправляем на главную
            if (window.location.pathname === '/login') {
                window.location.href = '/';
            } else {
                // Иначе обновляем интерфейс
                toggleAuthButtons(false);
                updateUserProfile();
            }
        } else {
            // Показываем сообщение об ошибке
            const loginError = document.getElementById('loginError');
            if (loginError) {
                loginError.classList.remove('d-none');
                loginError.textContent = 'Неверное имя пользователя или пароль';
            }
        }
    } catch (error) {
        console.error('Ошибка при входе:', error);
        
        // Показываем общее сообщение об ошибке
        const loginError = document.getElementById('loginError');
        if (loginError) {
            loginError.classList.remove('d-none');
            loginError.textContent = 'Произошла ошибка при попытке входа. Пожалуйста, попробуйте позже.';
        }
    }
}

/**
 * Обработка формы регистрации
 * @param {Event} event - событие отправки формы
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const agreeTerms = document.getElementById('agreeTerms').checked;
    
    // Проверка согласия с условиями
    if (!agreeTerms) {
        const registerError = document.getElementById('registerError');
        if (registerError) {
            registerError.classList.remove('d-none');
            registerError.textContent = 'Вы должны согласиться с условиями использования и политикой конфиденциальности';
        }
        return;
    }
    
    // Проверка совпадения паролей
    if (password !== confirmPassword) {
        const registerError = document.getElementById('registerError');
        if (registerError) {
            registerError.classList.remove('d-none');
            registerError.textContent = 'Пароли не совпадают';
        }
        return;
    }
    
    try {
        const response = await fetch('/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        
        if (response.ok) {
            // Перенаправляем на страницу входа с флагом успешной регистрации
            window.location.href = '/login?registered=true';
        } else {
            const data = await response.json();
            
            // Показываем сообщение об ошибке
            const registerError = document.getElementById('registerError');
            if (registerError) {
                registerError.classList.remove('d-none');
                registerError.textContent = data.detail || 'Ошибка при регистрации';
            }
        }
    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        
        // Показываем общее сообщение об ошибке
        const registerError = document.getElementById('registerError');
        if (registerError) {
            registerError.classList.remove('d-none');
            registerError.textContent = 'Произошла ошибка при попытке регистрации. Пожалуйста, попробуйте позже.';
        }
    }
}

/**
 * Обработка выхода из системы
 * @param {Event} event - событие клика
 */
function handleLogout(event) {
    event.preventDefault();
    
    // Удаляем токен из localStorage
    localStorage.removeItem('token');
    
    // Перенаправляем на главную страницу
    window.location.href = '/';
}

/**
 * Переключение видимости пароля
 * @param {Event} event - событие клика
 */
function togglePasswordVisibility(event) {
    const button = event.currentTarget;
    const inputGroup = button.closest('.input-group');
    const passwordInput = inputGroup.querySelector('input');
    const icon = button.querySelector('i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

/**
 * Проверка надежности пароля
 * @param {Event} event - событие ввода
 */
function validatePassword(event) {
    const password = event.target.value;
    const passwordFeedback = document.getElementById('passwordFeedback');
    
    if (!passwordFeedback) return;
    
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const isLongEnough = password.length >= 8;
    
    let errorMessage = '';
    
    if (!isLongEnough) {
        errorMessage = 'Пароль должен содержать минимум 8 символов';
    } else if (!(hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar)) {
        errorMessage = 'Пароль должен содержать заглавные и строчные буквы, цифры и специальные символы';
    }
    
    if (errorMessage) {
        passwordFeedback.textContent = errorMessage;
        passwordFeedback.classList.remove('d-none');
    } else {
        passwordFeedback.classList.add('d-none');
    }
}

/**
 * Проверка совпадения паролей
 * @param {Event} event - событие ввода
 */
function validatePasswordMatch(event) {
    const confirmPassword = event.target.value;
    const password = document.getElementById('password').value;
    const registerError = document.getElementById('registerError');
    
    if (!registerError) return;
    
    if (password !== confirmPassword) {
        registerError.textContent = 'Пароли не совпадают';
        registerError.classList.remove('d-none');
    } else {
        registerError.classList.add('d-none');
    }
}
