document.addEventListener('DOMContentLoaded', function() {
    // Проверяем доступность GSAP
    if (typeof gsap === 'undefined') {
        console.error('GSAP не найден. Убедитесь, что библиотека подключена.');
        return;
    }
    
    // Начальное состояние - элементы невидимы
    gsap.set('.login-form', { opacity: 0, y: 30 });
    gsap.set('.login-title', { opacity: 0, y: -20 });
    gsap.set('.login-subtitle', { opacity: 0 });
    gsap.set('.login-form .form-group', { opacity: 0, y: 20 });
    gsap.set('.login-form .btn-primary', { opacity: 0, scale: 0.9 });
    gsap.set('.login-form .register-link', { opacity: 0 });
    
    // Создаем временную линию для последовательной анимации
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    
    // Добавляем анимации в очередь
    tl.to('.login-title', { opacity: 1, y: 0, duration: 0.6 })
      .to('.login-subtitle', { opacity: 1, duration: 0.6 }, '-=0.3')
      .to('.login-form', { opacity: 1, y: 0, duration: 0.8 }, '-=0.4')
      .to('.login-form .form-group', { 
          opacity: 1, 
          y: 0, 
          duration: 0.5,
          stagger: 0.1
      }, '-=0.4')
      .to('.login-form .btn-primary', { 
          opacity: 1, 
          scale: 1, 
          duration: 0.5 
      }, '-=0.2')
      .to('.login-form .register-link', { opacity: 1, duration: 0.5 }, '-=0.3');
      
    // Обработчик отправки формы
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Анимируем кнопку при отправке
            gsap.to('.login-form .btn-primary', {
                scale: 0.95,
                duration: 0.2,
                repeat: 1,
                yoyo: true
            });
            
            // Очищаем предыдущие ошибки
            const errorMessage = document.getElementById('error-message');
            if (errorMessage) {
                errorMessage.style.display = 'none';
            }
            
            // Отправляем данные для входа
            api.login(username, password)
                .then(response => {
                    // Проверяем наличие токена
                    if (!response || !response.access_token) {
                        throw new Error('Не удалось получить токен авторизации');
                    }
                    
                    console.log('Успешный вход:', response);
                    
                    // Обновляем экземпляр API 
                    api.token = response.access_token;
                    api.user = {
                        id: response.user_id,
                        username: response.username,
                        email: response.email
                    };
                    
                    // Сохраняем также в localStorage для резервного варианта
                    localStorage.setItem('authToken', response.access_token);
                    
                    // Успешный вход - анимируем переход
                    gsap.to('.login-form', {
                        opacity: 0,
                        y: -30,
                        duration: 0.5,
                        onComplete: function() {
                            console.log('Перенаправление на /profile');
                            // Перенаправляем на страницу профиля
                            window.location.href = '/profile';
                        }
                    });
                })
                .catch(error => {
                    // Ошибка входа - показываем сообщение об ошибке
                    console.error('Ошибка входа:', error);
                    
                    // Анимируем форму для обозначения ошибки
                    gsap.to('.login-form', {
                        x: 10,
                        duration: 0.1,
                        repeat: 3,
                        yoyo: true
                    });
                    
                    // Показываем сообщение об ошибке
                    if (errorMessage) {
                        errorMessage.textContent = error.message || 'Неверное имя пользователя или пароль';
                        errorMessage.style.display = 'block';
                        
                        gsap.from(errorMessage, {
                            opacity: 0,
                            y: -10,
                            duration: 0.3
                        });
                    }
                });
        });
    }
}); 