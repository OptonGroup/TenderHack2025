document.addEventListener('DOMContentLoaded', function() {
    console.log('GSAP Animation: Initializing...');
    
    // Проверяем доступность GSAP
    if (typeof gsap === 'undefined') {
        console.error('GSAP не найден. Убедитесь, что библиотека подключена.');
        return;
    }
    
    // Проверяем доступность ScrollTrigger
    let hasScrollTrigger = true;
    if (typeof ScrollTrigger === 'undefined') {
        console.error('ScrollTrigger не найден. Анимации при прокрутке не будут работать.');
        hasScrollTrigger = false;
    } else {
        // Регистрируем плагин ScrollTrigger
        gsap.registerPlugin(ScrollTrigger);
        console.log('GSAP: ScrollTrigger plugin registered');
    }
    
    // Начальное состояние - устанавливаем начальные состояния для элементов
    console.log('GSAP: Setting initial states for hero elements');
    gsap.set('.hero-title', { opacity: 0, y: 50 });
    gsap.set('.hero-subtitle', { opacity: 0, y: 30 });
    gsap.set('.hero-section .btn', { opacity: 0, y: 20 });
    gsap.set('.hero-image', { opacity: 0, x: 50 });
    
    // Анимация для заголовка
    gsap.to('.hero-title', {
        duration: 1,
        y: 0,
        opacity: 1,
        ease: 'power3.out'
    });
    
    // Анимация для подзаголовка
    gsap.to('.hero-subtitle', {
        duration: 1,
        y: 0,
        opacity: 1,
        ease: 'power3.out',
        delay: 0.3
    });
    
    // Анимация для кнопок
    gsap.to('.hero-section .btn', {
        opacity: 1,
        y: 0,
        duration: 0.8,
        delay: 0.6,
        stagger: 0.2
    });
    
    // Анимация для изображения героя
    gsap.to('.hero-image', {
        opacity: 1,
        x: 0,
        duration: 1,
        delay: 0.8,
        onComplete: function() {
            console.log('GSAP: Hero animations completed');
        }
    });
    
    // Анимация статистики
    function animateStats() {
        console.log('GSAP: Initializing stats animations');
        const statsUsers = document.getElementById('stats-users');
        const statsTenders = document.getElementById('stats-tenders');
        const statsAccuracy = document.getElementById('stats-accuracy');
        
        if (!hasScrollTrigger) {
            // Упрощенная анимация без ScrollTrigger
            if (statsUsers) gsap.to(statsUsers, {
                innerHTML: 10000,
                duration: 2,
                snap: { innerHTML: 1 }
            });
            
            if (statsTenders) gsap.to(statsTenders, {
                innerHTML: 5000,
                duration: 2,
                snap: { innerHTML: 1 }
            });
            
            if (statsAccuracy) {
                gsap.to(statsAccuracy, {
                    innerHTML: 98,
                    duration: 2,
                    snap: { innerHTML: 1 },
                    onUpdate: function() {
                        statsAccuracy.innerHTML = Math.round(this.targets()[0].innerHTML) + '%';
                    }
                });
            }
            return;
        }
        
        if (statsUsers) {
            gsap.set(statsUsers, { innerHTML: 0 });
            
            gsap.to(statsUsers, {
                innerHTML: 10000,
                duration: 2,
                snap: { innerHTML: 1 },
                scrollTrigger: {
                    trigger: statsUsers,
                    start: 'top 80%',
                    once: true
                }
            });
        }
        
        if (statsTenders) {
            gsap.set(statsTenders, { innerHTML: 0 });
            
            gsap.to(statsTenders, {
                innerHTML: 5000,
                duration: 2,
                snap: { innerHTML: 1 },
                scrollTrigger: {
                    trigger: statsTenders,
                    start: 'top 80%',
                    once: true
                }
            });
        }
        
        if (statsAccuracy) {
            gsap.set(statsAccuracy, { innerHTML: 0 });
            
            gsap.to(statsAccuracy, {
                innerHTML: 98,
                duration: 2,
                snap: { innerHTML: 1 },
                scrollTrigger: {
                    trigger: statsAccuracy,
                    start: 'top 80%',
                    once: true
                },
                onUpdate: function() {
                    statsAccuracy.innerHTML = Math.round(this.targets()[0].innerHTML) + '%';
                }
            });
        }
    }
    
    // Параллакс для героического раздела
    function initParallax() {
        const heroSection = document.querySelector('.hero-section');
        const heroPattern = document.querySelector('.hero-pattern');
        
        if (heroSection && heroPattern) {
            document.addEventListener('mousemove', function(e) {
                const x = (window.innerWidth - e.pageX) / 100;
                const y = (window.innerHeight - e.pageY) / 100;
                
                gsap.to(heroPattern, {
                    x: x,
                    y: y,
                    duration: 1,
                    ease: 'power2.out'
                });
            });
        }
    }
    
    // Настраиваем анимации для элементов при прокрутке
    function setupScrollAnimations() {
        console.log('GSAP: Setting up scroll animations');
        
        if (!hasScrollTrigger) {
            console.log('GSAP: ScrollTrigger not available, using alternative animations');
            // Если ScrollTrigger недоступен, устанавливаем видимые состояния для всех элементов
            gsap.utils.toArray('.feature-card, .step, .stats-item, .testimonial-card, .scroll-trigger, .cta-section')
                .forEach(element => {
                    gsap.set(element, { opacity: 1, y: 0, x: 0, scale: 1 });
                });
            return;
        }
        
        // Анимация для карточек с преимуществами
        const featureCards = document.querySelectorAll('.feature-card');
        if (featureCards.length) {
            console.log('GSAP: Initializing feature cards animations, found:', featureCards.length);
            gsap.set(featureCards, { opacity: 0, y: 50 });
            
            ScrollTrigger.batch(featureCards, {
                start: 'top 80%',
                onEnter: batch => gsap.to(batch, {
                    opacity: 1,
                    y: 0,
                    stagger: 0.15,
                    duration: 0.8,
                    ease: 'power3.out'
                })
            });
        }
        
        // Анимация для шагов "Как это работает"
        const steps = document.querySelectorAll('.step');
        if (steps.length) {
            console.log('GSAP: Initializing steps animations, found:', steps.length);
            gsap.set(steps, { opacity: 0, x: -30 });
            
            ScrollTrigger.batch(steps, {
                start: 'top 80%',
                onEnter: batch => gsap.to(batch, {
                    opacity: 1,
                    x: 0,
                    stagger: 0.2,
                    duration: 0.8,
                    ease: 'power3.out'
                })
            });
        }
        
        // Анимация для блоков статистики
        const statsItems = document.querySelectorAll('.stats-item');
        if (statsItems.length) {
            console.log('GSAP: Initializing stats items animations, found:', statsItems.length);
            gsap.set(statsItems, { opacity: 0, y: 30 });
            
            ScrollTrigger.batch(statsItems, {
                start: 'top 80%',
                onEnter: batch => gsap.to(batch, {
                    opacity: 1,
                    y: 0,
                    stagger: 0.15,
                    duration: 0.8,
                    ease: 'power3.out'
                })
            });
        }
        
        // Анимация для карточек с отзывами
        const testimonialCards = document.querySelectorAll('.testimonial-card');
        if (testimonialCards.length) {
            console.log('GSAP: Initializing testimonial cards animations, found:', testimonialCards.length);
            gsap.set(testimonialCards, { opacity: 0, scale: 0.9 });
            
            ScrollTrigger.batch(testimonialCards, {
                start: 'top 80%',
                onEnter: batch => gsap.to(batch, {
                    opacity: 1,
                    scale: 1,
                    stagger: 0.15,
                    duration: 0.8,
                    ease: 'back.out(1.7)'
                })
            });
        }
        
        // Анимация для других элементов с классом scroll-trigger
        const scrollTriggers = document.querySelectorAll('.scroll-trigger');
        if (scrollTriggers.length) {
            console.log('GSAP: Initializing scroll trigger animations, found:', scrollTriggers.length);
            // Устанавливаем начальные значения для элементов
            scrollTriggers.forEach(element => {
                gsap.set(element, { opacity: 0, y: 30 });
            });
            
            // Создаем анимацию для каждого элемента по отдельности
            scrollTriggers.forEach(element => {
                ScrollTrigger.create({
                    trigger: element,
                    start: "top 80%",
                    onEnter: () => {
                        gsap.to(element, {
                            opacity: 1,
                            y: 0,
                            duration: 0.8,
                            ease: "power3.out"
                        });
                    },
                    once: true
                });
            });
        }
        
        // Анимация для CTA секции
        const ctaSection = document.querySelector('.cta-section');
        if (ctaSection) {
            console.log('GSAP: Initializing CTA section animation');
            gsap.set(ctaSection, { opacity: 0, y: 50 });
            
            ScrollTrigger.create({
                trigger: ctaSection,
                start: 'top 80%',
                onEnter: () => gsap.to(ctaSection, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: 'power3.out'
                })
            });
        }
    }
    
    // Инициализация всех анимаций
    animateStats();
    initParallax();
    setupScrollAnimations();
}); 