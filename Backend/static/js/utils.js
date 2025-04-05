// Utils.js - набор утилитарных функций и настроек GSAP анимаций

// Функция для переключения темной темы
function toggleTheme() {
  const body = document.body;
  const themeToggle = document.querySelector('.theme-toggle');
  
  if (body.getAttribute('data-theme') === 'dark') {
    body.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
    themeToggle.classList.remove('active');
  } else {
    body.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
    themeToggle.classList.add('active');
  }
}

// Функция для применения сохраненной темы при загрузке страницы
function applyStoredTheme() {
  const storedTheme = localStorage.getItem('theme');
  const themeToggle = document.querySelector('.theme-toggle');
  
  if (storedTheme === 'dark') {
    document.body.setAttribute('data-theme', 'dark');
    if (themeToggle) {
      themeToggle.classList.add('active');
    }
  }
}

// Функция для отображения toast-сообщений
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <span>${message}</span>
      <button class="toast-close">&times;</button>
    </div>
  `;
  
  document.body.appendChild(toast);
  
  // Анимация появления
  gsap.fromTo(toast, {
    opacity: 0,
    y: 20
  }, {
    opacity: 1,
    y: 0,
    duration: 0.3
  });
  
  // Закрытие по клику на крестик
  toast.querySelector('.toast-close').addEventListener('click', () => {
    gsap.to(toast, {
      opacity: 0,
      y: 20,
      duration: 0.3,
      onComplete: () => toast.remove()
    });
  });
  
  // Автоматическое закрытие через 5 секунд
  setTimeout(() => {
    if (document.body.contains(toast)) {
      gsap.to(toast, {
        opacity: 0,
        y: 20,
        duration: 0.3,
        onComplete: () => toast.remove()
      });
    }
  }, 5000);
}

// Функция для создания уникального ID чата
function generateChatId() {
  return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Функция для запроса к AI (заглушка)
async function requestAIResponse(message) {
  // Имитация задержки ответа от сервера
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Заглушка ответа от AI
  return {
    message: `Это автоматический ответ на ваше сообщение: "${message}". В будущем здесь будет реальный ответ от AI.`,
    id: Date.now()
  };
}

// Функция для распознавания речи
function startSpeechRecognition(onResult, onError) {
  // Проверяем поддержку браузером
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    console.error('Браузер не поддерживает SpeechRecognition API');
    showToast('Ваш браузер не поддерживает распознавание речи', 'error');
    if (onError) onError('Browser not supported');
    return null;
  }
  
  try {
    console.log('Инициализация распознавания речи');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'ru-RU';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;
    
    recognition.onstart = function() {
      console.log('Распознавание речи запущено');
    };
    
    recognition.onresult = function(event) {
      console.log('Получен результат распознавания', event);
      const result = event.results[0][0].transcript;
      console.log('Распознанный текст:', result);
      if (onResult) onResult(result);
    };
    
    recognition.onerror = function(event) {
      console.error('Ошибка распознавания речи:', event.error);
      if (onError) onError(event.error);
    };
    
    recognition.onend = function() {
      console.log('Завершено распознавание речи');
    };
    
    // Запускаем распознавание
    console.log('Запуск распознавания речи...');
    recognition.start();
    return recognition;
  } catch (error) {
    console.error('Ошибка при инициализации распознавания речи:', error);
    if (onError) onError(error.message);
    return null;
  }
}

// Инициализация анимаций GSAP для страницы
function initPageAnimations() {
  // Анимация появления элементов при загрузке страницы
  gsap.to('.animated-element', {
    opacity: 1,
    y: 0,
    stagger: 0.1,
    duration: 0.5,
    ease: 'power2.out'
  });
  
  // Инициализация ScrollTrigger для элементов, которые должны анимироваться при прокрутке
  if (typeof ScrollTrigger !== 'undefined') {
    gsap.utils.toArray('.scroll-trigger').forEach((section) => {
      gsap.fromTo(section, 
        {
          opacity: 0,
          y: 50
        },
        {
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
            markers: false
          },
          opacity: 1,
          y: 0,
          duration: 0.7,
          ease: 'power2.out'
        }
      );
    });
  }
}

// Функция валидации формы
function validateForm(form) {
  const inputs = form.querySelectorAll('input, textarea, select');
  let isValid = true;
  
  inputs.forEach(input => {
    // Пропускаем скрытые и необязательные поля
    if (input.type === 'hidden' || !input.hasAttribute('required')) {
      return;
    }
    
    let errorMessage = '';
    
    // Проверка на заполненность
    if (!input.value.trim()) {
      errorMessage = 'Это поле обязательно для заполнения';
      isValid = false;
    }
    
    // Валидация email
    if (input.type === 'email' && input.value.trim()) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(input.value)) {
        errorMessage = 'Введите корректный email адрес';
        isValid = false;
      }
    }
    
    // Валидация пароля
    if (input.type === 'password' && input.id === 'password' && input.value.trim()) {
      if (input.value.length < 6) {
        errorMessage = 'Пароль должен содержать не менее 6 символов';
        isValid = false;
      }
    }
    
    // Валидация подтверждения пароля
    if (input.type === 'password' && input.id === 'confirm-password' && input.value.trim()) {
      const passwordInput = form.querySelector('#password');
      if (passwordInput && input.value !== passwordInput.value) {
        errorMessage = 'Пароли не совпадают';
        isValid = false;
      }
    }
    
    // Отображение ошибки
    const errorElement = input.nextElementSibling;
    if (errorElement && errorElement.classList.contains('error-message')) {
      errorElement.textContent = errorMessage;
      errorElement.style.display = errorMessage ? 'block' : 'none';
      
      if (errorMessage) {
        input.classList.add('is-invalid');
      } else {
        input.classList.remove('is-invalid');
      }
    }
  });
  
  return isValid;
}

// Функция для форматирования даты
function formatDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  applyStoredTheme();
  
  // Обработчик для переключателя темы
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  
  // Инициализация анимаций
  if (typeof gsap !== 'undefined') {
    initPageAnimations();
  }
  
  // Инициализация тултипов Bootstrap если они есть
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
}); 