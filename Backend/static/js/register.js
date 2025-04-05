document.addEventListener('DOMContentLoaded', function() {
    // Проверяем доступность GSAP
    if (typeof gsap === 'undefined') {
        console.error('GSAP не найден. Убедитесь, что библиотека подключена.');
        return;
    }
    
    // Начальное состояние - элементы невидимы
    gsap.set('.register-form', { opacity: 0, y: 30 });
    gsap.set('.register-title', { opacity: 0, y: -20 });
    gsap.set('.register-subtitle', { opacity: 0 });
    gsap.set('.register-form .form-group', { opacity: 0, y: 20 });
    gsap.set('.register-form .btn-primary', { opacity: 0, scale: 0.9 });
    gsap.set('.register-form .login-link', { opacity: 0 });
    
    // Создаем временную линию для последовательной анимации
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    
    // Добавляем анимации в очередь
    tl.to('.register-title', { opacity: 1, y: 0, duration: 0.6 })
      .to('.register-subtitle', { opacity: 1, duration: 0.6 }, '-=0.3')
      .to('.register-form', { opacity: 1, y: 0, duration: 0.8 }, '-=0.4')
      .to('.register-form .form-group', { 
          opacity: 1, 
          y: 0, 
          duration: 0.5,
          stagger: 0.1
      }, '-=0.4')
      .to('.register-form .btn-primary', { 
          opacity: 1, 
          scale: 1, 
          duration: 0.5 
      }, '-=0.2')
      .to('.register-form .login-link', { opacity: 1, duration: 0.5 }, '-=0.3');
      
    // Обработчик отправки формы
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password-confirm').value;
            
            // Валидация пароля
            if (password !== passwordConfirm) {
                // Пароли не совпадают - показываем ошибку
                const errorMessage = document.getElementById('error-message');
                if (errorMessage) {
                    errorMessage.textContent = 'Пароли не совпадают';
                    errorMessage.style.display = 'block';
                    
                    gsap.from(errorMessage, {
                        opacity: 0,
                        y: -10,
                        duration: 0.3
                    });
                }
                
                // Анимируем поля с паролями для обозначения ошибки
                gsap.to('#password, #password-confirm', {
                    borderColor: '#dc3545',
                    duration: 0.3
                });
                
                return;
            }
            
            // Анимируем кнопку при отправке
            gsap.to('.register-form .btn-primary', {
                scale: 0.95,
                duration: 0.2,
                repeat: 1,
                yoyo: true
            });
            
            // Отправляем данные для регистрации
            api.register(username, email, password)
                .then(response => {
                    // Успешная регистрация - анимируем переход к форме входа
                    gsap.to('.register-form', {
                        opacity: 0,
                        y: -30,
                        duration: 0.5,
                        onComplete: function() {
                            window.location.href = '/login';
                        }
                    });
                })
                .catch(error => {
                    // Ошибка регистрации - показываем сообщение об ошибке
                    console.error('Ошибка регистрации:', error);
                    
                    // Анимируем форму для обозначения ошибки
                    gsap.to('.register-form', {
                        x: 10,
                        duration: 0.1,
                        repeat: 3,
                        yoyo: true
                    });
                    
                    // Показываем сообщение об ошибке
                    const errorMessage = document.getElementById('error-message');
                    if (errorMessage) {
                        errorMessage.textContent = error.message || 'Ошибка регистрации. Попробуйте другие данные.';
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