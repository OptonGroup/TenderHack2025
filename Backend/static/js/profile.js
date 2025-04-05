/**
 * Файл для работы с профилем пользователя
 * Обработка форм и взаимодействие с API
 */

// API URL
const API_BASE_URL = 'http://localhost:8000/api';

// Токен авторизации
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');

// DOM элементы
document.addEventListener('DOMContentLoaded', function() {
    // Проверка авторизации
    if (!authToken) {
        // Перенаправление на страницу входа, если пользователь не авторизован
        window.location.href = 'login.html';
        return;
    }
    
    // Загрузка данных пользователя
    loadUserProfile();
    
    // Инициализация GSAP анимаций
    initAnimations();
    
    // Настройка обработчиков форм
    setupFormHandlers();
});

/**
 * Инициализация GSAP анимаций
 */
function initAnimations() {
    // Анимация карточек профиля
    gsap.from('.card', {
        duration: 0.6,
        y: 20,
        opacity: 0,
        stagger: 0.2,
        ease: 'power2.out'
    });
}

/**
 * Загрузка данных профиля пользователя
 */
async function loadUserProfile() {
    try {
        const userData = await fetchCurrentUser();
        
        if (userData) {
            // Обновление информации о пользователе в профиле
            updateProfileFields(userData);
        } else {
            // Если не удалось получить данные, перенаправление на страницу входа
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Ошибка при загрузке профиля:', error);
        showError('Не удалось загрузить данные профиля. Пожалуйста, обновите страницу.');
    }
}

/**
 * Обновление полей в форме профиля
 * @param {Object} userData - Данные пользователя
 */
function updateProfileFields(userData) {
    document.getElementById('profileUsername').value = userData.username || '';
    document.getElementById('profileEmail').value = userData.email || '';
    
    // Обновление имени и фамилии
    const nameParts = userData.username.split(' ');
    if (nameParts.length > 1) {
        document.getElementById('profileFirstName').value = nameParts[0] || '';
        document.getElementById('profileLastName').value = nameParts.slice(1).join(' ') || '';
    } else {
        document.getElementById('profileFirstName').value = userData.username || '';
    }
    
    // Обновление отображаемого имени в шапке
    document.getElementById('userName').textContent = userData.username;
    document.getElementById('profileUserName').textContent = userData.username;
}

/**
 * Настройка обработчиков форм
 */
function setupFormHandlers() {
    // Форма обновления профиля
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
    
    // Форма изменения пароля
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordUpdate);
    }
    
    // Обработчики переключения видимости пароля
    setupPasswordToggles();
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
 * Обработчик обновления профиля
 * @param {Event} event - Событие отправки формы
 */
async function handleProfileUpdate(event) {
    event.preventDefault();
    
    // Получение значений полей формы
    const firstName = document.getElementById('profileFirstName').value;
    const lastName = document.getElementById('profileLastName').value;
    const email = document.getElementById('profileEmail').value;
    const company = document.getElementById('profileCompany').value;
    const phone = document.getElementById('profilePhone').value;
    const bio = document.getElementById('profileBio').value;
    
    try {
        // Формирование полного имени
        const fullName = lastName ? `${firstName} ${lastName}` : firstName;
        
        // Обновление данных пользователя
        const response = await fetch(`${API_BASE_URL}/users/${currentUser.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                username: fullName,
                email: email,
                company: company,
                phone: phone,
                bio: bio
            })
        });
        
        if (response.ok) {
            // Обновление данных в localStorage
            const updatedUser = {
                ...currentUser,
                username: fullName,
                email: email
            };
            localStorage.setItem('currentUser', JSON.stringify(updatedUser));
            
            // Обновление данных на странице
            document.getElementById('userName').textContent = fullName;
            document.getElementById('profileUserName').textContent = fullName;
            
            // Уведомление об успешном обновлении
            showSuccess('Данные профиля успешно обновлены');
        } else {
            // Отображение ошибки
            const errorData = await response.json();
            showError(errorData.detail || 'Ошибка при обновлении профиля');
        }
    } catch (error) {
        console.error('Ошибка при обновлении профиля:', error);
        showError('Ошибка сервера. Пожалуйста, попробуйте позже.');
    }
}

/**
 * Обработчик изменения пароля
 * @param {Event} event - Событие отправки формы
 */
async function handlePasswordUpdate(event) {
    event.preventDefault();
    
    // Получение значений полей формы
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    
    // Проверка совпадения паролей
    if (newPassword !== confirmNewPassword) {
        showError('Новые пароли не совпадают');
        return;
    }
    
    try {
        // Изменение пароля
        const response = await fetch(`${API_BASE_URL}/users/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        if (response.ok) {
            // Очистка полей формы
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmNewPassword').value = '';
            
            // Уведомление об успешном изменении
            showSuccess('Пароль успешно изменен');
        } else {
            // Отображение ошибки
            const errorData = await response.json();
            showError(errorData.detail || 'Ошибка при изменении пароля');
        }
    } catch (error) {
        console.error('Ошибка при изменении пароля:', error);
        showError('Ошибка сервера. Пожалуйста, попробуйте позже.');
    }
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
            logout();
        }
        return null;
    } catch (error) {
        console.error('Ошибка при получении данных пользователя:', error);
        return null;
    }
}

/**
 * Выход из системы
 */
function logout() {
    // Удаление данных авторизации
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    // Перенаправление на главную страницу
    window.location.href = 'index.html';
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