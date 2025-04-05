// Константы для API
const API_BASE_URL = '/api';

// API эндпоинты
const API_ENDPOINTS = {
    LOGIN: `${API_BASE_URL}/login`,
    REGISTER: `${API_BASE_URL}/register`,
    USER: `${API_BASE_URL}/users/me`,
    CATEGORIES: `${API_BASE_URL}/categories`,
    TENDERS: `${API_BASE_URL}/tenders`,
    TENDER: (id) => `${API_BASE_URL}/tenders/${id}`,
    DOCUMENTS: `${API_BASE_URL}/documents`,
    TENDER_DOCUMENTS: (id) => `${API_BASE_URL}/tenders/${id}/documents`,
    BIDS: `${API_BASE_URL}/bids`,
    TENDER_BIDS: (id) => `${API_BASE_URL}/tenders/${id}/bids`,
    CHAT_HISTORY: `${API_BASE_URL}/chat-history`,
    CHAT_CONVERSATION: (chatId) => `${API_BASE_URL}/chat-history/${chatId}`,
    FINISH_CHAT: (chatId) => `${API_BASE_URL}/chat-history/${chatId}/finish`,
    DATA: `${API_BASE_URL}/data`,
    DATA_ITEM: (id) => `${API_BASE_URL}/data/${id}`,
    IMPORT_PARQUET: `${API_BASE_URL}/import-parquet`
};

// Класс для работы с API
class API {
    constructor() {
        this.token = localStorage.getItem('authToken') || null;
        this.user = null;
    }

    async login(username, password) {
        try {
            const response = await fetch(API_ENDPOINTS.LOGIN, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка авторизации');
            }

            const data = await response.json();
            
            // Сохраняем токен и данные пользователя
            this.token = data.access_token;
            this.user = {
                id: data.user_id,
                username: data.username,
                email: data.email
            };

            // Сохраняем токен в localStorage
            localStorage.setItem('authToken', this.token);
            
            console.log('Авторизация успешна:', { token: this.token, user: this.user });
            return data;
        } catch (error) {
            console.error('Ошибка при авторизации:', error);
            throw error;
        }
    }

    async register(username, email, password) {
        try {
            const response = await fetch(API_ENDPOINTS.REGISTER, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Ошибка регистрации');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка при регистрации:', error);
            throw error;
        }
    }

    async logout() {
        // Очищаем данные из памяти
        this.token = null;
        this.user = null;
        localStorage.removeItem('authToken');
        
        // Перенаправляем на /logout для очистки cookie
        window.location.href = '/logout';
    }

    isAuthenticated() {
        return !!this.token;
    }

    async getUser() {
        if (!this.token) {
            console.log('getUser: Нет токена, пользователь не авторизован');
            return null;
        }

        try {
            console.log('getUser: Запрос данных пользователя с токеном');
            const response = await fetch(API_ENDPOINTS.USER, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'  // Важно для работы с куками, если они используются
            });

            console.log('getUser: Ответ от сервера:', response.status, response.statusText);

            if (!response.ok) {
                const responseText = await response.text();
                console.error('getUser: Ошибка запроса:', response.status, responseText);
                
                if (response.status === 401) {
                    console.error('getUser: Недействительный токен, выход из системы');
                    // Если это не API запрос, а HTML страница, просто перенаправляем
                    if (responseText.includes('<!DOCTYPE html>')) {
                        window.location.href = '/login';
                        return null;
                    }
                    this.logout();
                    return null;
                }
                
                try {
                    const errorData = JSON.parse(responseText);
                    throw new Error(errorData.detail || 'Ошибка получения данных пользователя');
                } catch (e) {
                    throw new Error(`Ошибка получения данных пользователя: ${responseText}`);
                }
            }

            this.user = await response.json();
            console.log('getUser: Данные пользователя получены успешно:', this.user);
            return this.user;
        } catch (error) {
            console.error('getUser: Ошибка при получении данных пользователя:', error);
            return null;
        }
    }

    async getCategories() {
        try {
            const response = await fetch(API_ENDPOINTS.CATEGORIES);
            if (!response.ok) {
                throw new Error('Ошибка получения категорий');
            }
            return await response.json();
        } catch (error) {
            console.error('Ошибка при получении категорий:', error);
            throw error;
        }
    }

    async getTenders(params = {}) {
        try {
            const queryParams = new URLSearchParams(params).toString();
            const url = queryParams ? `${API_ENDPOINTS.TENDERS}?${queryParams}` : API_ENDPOINTS.TENDERS;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Ошибка получения тендеров');
            }
            return await response.json();
        } catch (error) {
            console.error('Ошибка при получении тендеров:', error);
            throw error;
        }
    }

    async getTender(id) {
        try {
            const response = await fetch(API_ENDPOINTS.TENDER(id));
            if (!response.ok) {
                throw new Error('Ошибка получения тендера');
            }
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при получении тендера ${id}:`, error);
            throw error;
        }
    }

    async createTender(tenderData) {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(API_ENDPOINTS.TENDERS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(tenderData)
            });

            if (!response.ok) {
                throw new Error('Ошибка создания тендера');
            }
            return await response.json();
        } catch (error) {
            console.error('Ошибка при создании тендера:', error);
            throw error;
        }
    }

    async updateTender(id, tenderData) {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(API_ENDPOINTS.TENDER(id), {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(tenderData)
            });

            if (!response.ok) {
                throw new Error('Ошибка обновления тендера');
            }
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при обновлении тендера ${id}:`, error);
            throw error;
        }
    }

    async getBids() {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(API_ENDPOINTS.BIDS, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Ошибка получения заявок');
            }
            return await response.json();
        } catch (error) {
            console.error('Ошибка при получении заявок:', error);
            throw error;
        }
    }

    async getTenderBids(tenderId) {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(API_ENDPOINTS.TENDER_BIDS(tenderId), {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Ошибка получения заявок на тендер');
            }
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при получении заявок на тендер ${tenderId}:`, error);
            throw error;
        }
    }

    async createBid(bidData) {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(API_ENDPOINTS.BIDS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(bidData)
            });

            if (!response.ok) {
                throw new Error('Ошибка создания заявки');
            }
            return await response.json();
        } catch (error) {
            console.error('Ошибка при создании заявки:', error);
            throw error;
        }
    }

    async updateBidStatus(bidId, status) {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(`${API_ENDPOINTS.BIDS}/${bidId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ status })
            });

            if (!response.ok) {
                throw new Error('Ошибка обновления статуса заявки');
            }
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при обновлении статуса заявки ${bidId}:`, error);
            throw error;
        }
    }

    async getUserChats() {
        if (!this.token) {
            console.log('getUserChats: Нет токена для получения списка чатов');
            return [];
        }

        try {
            console.log('getUserChats: Запрос списка чатов пользователя');
            const response = await fetch(API_ENDPOINTS.CHAT_HISTORY, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            console.log('getUserChats: Ответ сервера:', response.status, response.statusText);

            if (!response.ok) {
                if (response.status === 401) {
                    console.log('getUserChats: Ошибка авторизации, но продолжаем работу');
                    return [];
                }
                console.error('getUserChats: Ошибка запроса:', await response.text());
                return [];
            }
            
            const data = await response.json();
            console.log('getUserChats: Получены данные:', data);
            return data;
        } catch (error) {
            console.error('Ошибка при получении списка чатов:', error);
            return [];
        }
    }

    async getChatHistory(chatId) {
        if (!this.token) {
            console.log('getChatHistory: Нет токена, возвращаем пустой результат');
            return { chat_id: chatId, messages: [] };
        }

        try {
            console.log('getChatHistory: Запрос истории чата', chatId);
            const response = await fetch(API_ENDPOINTS.CHAT_CONVERSATION(chatId), {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            console.log('getChatHistory: Ответ сервера:', response.status);

            if (!response.ok) {
                if (response.status === 401 || response.status === 404) {
                    console.log('getChatHistory: Чат не найден или ошибка авторизации, возвращаем пустой результат');
                    return { chat_id: chatId, messages: [] };
                }
                console.error('getChatHistory: Ошибка запроса:', await response.text());
                return { chat_id: chatId, messages: [] };
            }

            const data = await response.json();
            console.log('getChatHistory: Получены данные:', data);
            return data;
        } catch (error) {
            console.error(`Ошибка при получении истории чата ${chatId}:`, error);
            return { chat_id: chatId, messages: [] };
        }
    }

    async sendMessage(chatId, message, isBot = false) {
        if (!this.token) {
            console.log('sendMessage: Нет токена, возвращаем заглушку');
            return { 
                id: Date.now(),
                chat_id: chatId, 
                message: message, 
                is_bot: isBot, 
                timestamp: new Date().toISOString() 
            };
        }

        try {
            if (!this.user) {
                const user = await this.getUser();
                if (!user) {
                    console.log('sendMessage: Пользователь не получен, возвращаем заглушку');
                    return { 
                        id: Date.now(),
                        chat_id: chatId, 
                        message: message, 
                        is_bot: isBot, 
                        timestamp: new Date().toISOString() 
                    };
                }
            }

            console.log('sendMessage: Отправка сообщения в чат', chatId);
            const response = await fetch(API_ENDPOINTS.CHAT_HISTORY, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    chat_id: chatId,
                    user_id: this.user.id,
                    message: message,
                    is_bot: isBot
                })
            });

            console.log('sendMessage: Ответ сервера:', response.status);

            if (!response.ok) {
                const responseText = await response.text();
                console.error('sendMessage: Ошибка запроса:', responseText);
                
                if (response.status === 401) {
                    console.log('sendMessage: Ошибка авторизации, возвращаем заглушку');
                    return { 
                        id: Date.now(),
                        chat_id: chatId, 
                        message: message, 
                        is_bot: isBot, 
                        timestamp: new Date().toISOString() 
                    };
                }
                
                throw new Error('Ошибка отправки сообщения');
            }

            const data = await response.json();
            console.log('sendMessage: Сообщение отправлено успешно:', data);
            return data;
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
            return { 
                id: Date.now(),
                chat_id: chatId, 
                message: message, 
                is_bot: isBot, 
                timestamp: new Date().toISOString() 
            };
        }
    }

    // Алиас для метода sendMessage для совместимости
    async sendChatMessage(chatId, message, isBot = false) {
        return this.sendMessage(chatId, message, isBot);
    }

    async finishChat(chatId, rating, comment = '') {
        if (!this.token) {
            console.log('finishChat: Нет токена, возвращаем заглушку');
            return { success: false, error: 'Требуется авторизация' };
        }

        try {
            console.log('finishChat: Завершение чата', chatId);
            const response = await fetch(API_ENDPOINTS.FINISH_CHAT(chatId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    rating,
                    comment
                })
            });

            console.log('finishChat: Ответ сервера:', response.status);

            if (!response.ok) {
                const responseText = await response.text();
                console.error('finishChat: Ошибка запроса:', responseText);
                
                if (response.status === 401) {
                    console.log('finishChat: Ошибка авторизации, возвращаем заглушку');
                    return { success: false, error: 'Требуется авторизация' };
                }
                
                if (response.status === 404) {
                    console.log('finishChat: Чат не найден, возвращаем заглушку');
                    return { success: true, message: 'Чат успешно завершен (не найден)' };
                }
                
                return { success: false, error: 'Ошибка завершения чата' };
            }

            const data = await response.json();
            console.log('finishChat: Чат успешно завершен:', data);
            return data;
        } catch (error) {
            console.error(`Ошибка при завершении чата ${chatId}:`, error);
            return { success: false, error: 'Ошибка завершения чата' };
        }
    }

    async deleteChat(chatId) {
        if (!this.token) {
            throw new Error('Требуется авторизация');
        }

        try {
            const response = await fetch(API_ENDPOINTS.CHAT_CONVERSATION(chatId), {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Ошибка удаления чата');
            }
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при удалении чата ${chatId}:`, error);
            throw error;
        }
    }

    async getData(params = {}) {
        try {
            const queryParams = new URLSearchParams(params).toString();
            const url = queryParams ? `${API_ENDPOINTS.DATA}?${queryParams}` : API_ENDPOINTS.DATA;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Ошибка получения данных');
            }
            return await response.json();
        } catch (error) {
            console.error('Ошибка при получении данных:', error);
            throw error;
        }
    }

    async getDataItem(id) {
        try {
            const response = await fetch(API_ENDPOINTS.DATA_ITEM(id));
            if (!response.ok) {
                throw new Error('Ошибка получения данных');
            }
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при получении данных ${id}:`, error);
            throw error;
        }
    }

    /**
     * Получить список всех пользователей (только для администратора)
     * @returns {Promise<Array>} Список пользователей
     */
    async getUsers() {
        try {
            const response = await fetch('/api/users', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching users:', error);
            throw error;
        }
    }
    
    /**
     * Изменить роль пользователя (только для администратора)
     * @param {Number} userId - ID пользователя
     * @param {String} role - Новая роль (user, operator, admin)
     * @returns {Promise<Object>} Обновленный пользователь
     */
    async updateUserRole(userId, role) {
        try {
            const response = await fetch(`/api/users/${userId}/role`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ role }),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating user role:', error);
            throw error;
        }
    }
    
    /**
     * Получить список заявок на поддержку (для операторов и администраторов)
     * @returns {Promise<Array>} Список активных заявок
     */
    async getSupportRequests() {
        try {
            const response = await fetch('/api/support-requests', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Accept': 'application/json'
                },
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching support requests:', error);
            throw error;
        }
    }
    
    /**
     * Отметить заявку на поддержку как решенную
     * @param {String} chatId - ID чата
     * @returns {Promise<Object>} Результат операции
     */
    async resolveSupportRequest(chatId) {
        try {
            const response = await fetch(`/api/support-requests/${chatId}/resolve`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error resolving support request:', error);
            throw error;
        }
    }
    
    /**
     * Отправить запрос оператору
     * @param {String} chatId - ID чата
     * @param {String} message - Сообщение для оператора
     * @returns {Promise<Object>} Созданное сообщение
     */
    async requestOperatorHelp(chatId, message) {
        try {
            const payload = {
                message,
                is_bot: false,
                message_metadata: {
                    operator_request: true,
                    request_timestamp: new Date().toISOString()
                }
            };
            
            const response = await fetch(`/api/chat-history/${chatId}/messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error requesting operator help:', error);
            throw error;
        }
    }
}

// Создаем глобальный экземпляр API
const api = new API();

// Проверяем авторизацию при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Инициализация API на странице:', window.location.pathname);
    console.log('Текущий токен:', api.token ? 'Токен присутствует' : 'Токен отсутствует');
    
    // Отложенная инициализация для предотвращения проблем с загрузкой
    setTimeout(() => {
        initializeAuth();
    }, 200);
    
    function initializeAuth() {
        // Проверяем авторизацию в зависимости от текущего пути
        const protectedPaths = ['/profile', '/chat'];
        const currentPath = window.location.pathname;
        
        console.log('Проверка авторизации для пути:', currentPath);
        console.log('Статус авторизации:', api.isAuthenticated() ? 'Авторизован' : 'Не авторизован');
        
        if (protectedPaths.includes(currentPath)) {
            console.log('Защищенный путь. Проверка авторизации...');
            if (!api.isAuthenticated()) {
                console.log('Пользователь не авторизован. Перенаправление на страницу входа.');
                // Если пользователь пытается получить доступ к защищенной странице без авторизации
                window.location.href = '/login';
            } else {
                console.log('Пользователь авторизован. Получение данных...');
                // Если пользователь авторизован, получаем его данные
                api.getUser()
                    .then(user => {
                        console.log('Данные пользователя успешно получены:', user);
                        
                        // Если на странице есть элементы с информацией о пользователе, обновляем их
                        if (document.getElementById('profile-username')) {
                            document.getElementById('profile-username').textContent = user.username;
                        }
                        if (document.getElementById('profile-email')) {
                            document.getElementById('profile-email').textContent = user.email;
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка при получении данных пользователя:', error);
                        
                        // Показываем сообщение об ошибке, если существует элемент для ошибок
                        if (document.getElementById('error-message')) {
                            const errorElement = document.getElementById('error-message');
                            errorElement.textContent = 'Ошибка авторизации. Пожалуйста, войдите снова.';
                            errorElement.style.display = 'block';
                        }
                        
                        // Если получение данных пользователя не удалось, выходим из системы
                        api.logout();
                        
                        // Перенаправляем на страницу входа
                        console.log('Перенаправление на страницу входа из-за ошибки авторизации.');
                        window.location.href = '/login';
                    });
            }
        } else if (api.isAuthenticated()) {
            // Даже на незащищенных страницах, если есть токен, проверяем его
            console.log('Незащищенный путь, но пользователь авторизован. Обновление данных пользователя.');
            api.getUser().catch(error => {
                console.error('Ошибка при обновлении данных пользователя:', error);
            });
        }
    }
}); 