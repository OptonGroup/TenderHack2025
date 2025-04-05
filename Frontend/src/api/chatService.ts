// Типы данных для работы с API
export interface UserMessage {
  content: string;
}

export interface BotResponse {
  id: string;
  content: string;
  source?: string;
  timestamp: string;
}

export interface ChatHistoryItem {
  id: string;
  question: string;
  answer: string;
  date: string;
  rating: 'positive' | 'negative' | null;
}

export interface FeedbackRequest {
  messageId: string;
  type: 'positive' | 'negative' | null;
}

export interface ChatRatingRequest {
  rating: number;  // От 1 до 5
  comment?: string;
}

// Базовый URL API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Функция для получения токена аутентификации
const getAuthToken = () => {
  return localStorage.getItem('token') || '';
};

// Проверка, используем ли мы моки или реальный API
const USE_MOCK_API = process.env.REACT_APP_USE_MOCK_API === 'true';

// Преобразование ChatHistory в формат, удобный для фронтенда
const formatChatHistory = (historyFromApi: any[]): ChatHistoryItem[] => {
  // Группировка сообщений по паре вопрос-ответ
  const groupedMessages: Record<string, any[]> = {};
  
  historyFromApi.forEach(msg => {
    if (!groupedMessages[msg.chat_id]) {
      groupedMessages[msg.chat_id] = [];
    }
    groupedMessages[msg.chat_id].push(msg);
  });
  
  // Формирование элементов истории
  return Object.keys(groupedMessages).map(chatId => {
    const messages = groupedMessages[chatId].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    
    // Ищем первое сообщение пользователя (вопрос)
    const userMessage = messages.find(m => !m.is_bot);
    // Ищем первый ответ бота
    const botMessage = messages.find(m => m.is_bot);
    
    // Извлекаем рейтинг из метаданных
    let rating: 'positive' | 'negative' | null = null;
    if (botMessage && botMessage.message_metadata && botMessage.message_metadata.feedback) {
      rating = botMessage.message_metadata.feedback as 'positive' | 'negative';
    }
    
    return {
      id: chatId,
      question: userMessage ? userMessage.message : '',
      answer: botMessage ? botMessage.message : '',
      date: botMessage ? botMessage.timestamp : new Date().toISOString(),
      rating: rating
    };
  });
};

// Сервис для работы с API чата
const chatService = {
  /**
   * Отправляет сообщение пользователя и получает ответ от бота
   * @param message - Сообщение пользователя
   * @returns Ответ от бота
   */
  async sendMessage(message: UserMessage): Promise<BotResponse> {
    try {
      if (!USE_MOCK_API) {
        const userId = localStorage.getItem('user_id') || '1'; // Используем ID пользователя из localStorage
        const chatId = localStorage.getItem('current_chat_id') || Date.now().toString();
        
        // Сохраняем ID текущего чата
        localStorage.setItem('current_chat_id', chatId);
        
        // Сохраняем сообщение пользователя
        const userMessageData = {
          user_id: parseInt(userId),
          chat_id: chatId,
          message: message.content,
          is_bot: false,
          message_metadata: {}
        };
        
        await fetch(`${API_URL}/api/chat-history`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          },
          body: JSON.stringify(userMessageData),
        });
        
        // Имитируем задержку обработки запроса
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Формируем ответ бота на основе контента сообщения
        const botContent = this.getMockResponse(message.content);
        const botSource = this.getMockSource(message.content);
        
        // Сохраняем ответ бота
        const botMessageData = {
          user_id: parseInt(userId),
          chat_id: chatId,
          message: botContent,
          is_bot: true,
          message_metadata: {
            source: botSource,
            feedback: null
          }
        };
        
        const botResponse = await fetch(`${API_URL}/api/chat-history`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          },
          body: JSON.stringify(botMessageData),
        });
        
        const botData = await botResponse.json();
        
        return {
          id: botData.id.toString(),
          content: botContent,
          source: botSource,
          timestamp: new Date().toISOString()
        };
      } else {
        // Используем мок-ответ, если API недоступен
        return new Promise(resolve => {
          setTimeout(() => {
            resolve({
              id: Date.now().toString(),
              content: this.getMockResponse(message.content),
              source: this.getMockSource(message.content),
              timestamp: new Date().toISOString()
            });
          }, 1000);
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // В случае ошибки используем мок-ответ
      return {
        id: Date.now().toString(),
        content: this.getMockResponse(message.content),
        source: this.getMockSource(message.content),
        timestamp: new Date().toISOString()
      };
    }
  },

  /**
   * Получает историю чата пользователя
   * @returns Список элементов истории чата
   */
  async getChatHistory(): Promise<ChatHistoryItem[]> {
    try {
      if (!USE_MOCK_API) {
        const response = await fetch(`${API_URL}/api/chat-history`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch chat history');
        }
        
        const chatIds = await response.json();
        
        // Если нет истории чатов, возвращаем пустой массив
        if (!chatIds || chatIds.length === 0) {
          return [];
        }
        
        // Получаем детали для каждого чата
        const chatDetailsPromises = chatIds.map((chatId: string) => 
          fetch(`${API_URL}/api/chat-history/${chatId}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${getAuthToken()}`
            },
          }).then(res => res.json())
        );
        
        const chatsDetails = await Promise.all(chatDetailsPromises);
        
        // Преобразуем в формат, понятный для фронтенда
        return formatChatHistory(chatsDetails.flatMap(chat => chat.messages));
      } else {
        // Используем моки, если API недоступен
        return new Promise(resolve => {
          setTimeout(() => {
            resolve([
              {
                id: '1',
                question: 'Как зарегистрироваться на портале?',
                answer: 'Для регистрации на Портале поставщиков вам необходимо: 1) подготовить электронную подпись, 2) заполнить форму регистрации на сайте, 3) подтвердить данные компании.',
                date: new Date(Date.now() - 3600000 * 24).toISOString(),
                rating: 'positive'
              },
              {
                id: '2',
                question: 'Как подать заявку на тендер?',
                answer: 'Для подачи заявки на тендер вам необходимо выбрать интересующую закупку из каталога, ознакомиться с требованиями и нажать кнопку "Подать заявку".',
                date: new Date(Date.now() - 3600000 * 12).toISOString(),
                rating: 'negative'
              },
              {
                id: '3',
                question: 'Когда происходит оплата по контракту?',
                answer: 'Порядок оплаты по контракту устанавливается заказчиком в соответствии с 44-ФЗ. Обычно оплата производится в течение 15 рабочих дней с момента подписания акта выполненных работ.',
                date: new Date(Date.now() - 3600000 * 5).toISOString(),
                rating: null
              }
            ]);
          }, 500);
        });
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
      // В случае ошибки возвращаем пустой массив
      return [];
    }
  },

  /**
   * Отправляет обратную связь о сообщении бота
   * @param feedback - Данные обратной связи
   */
  async sendFeedback(feedback: FeedbackRequest): Promise<void> {
    try {
      if (!USE_MOCK_API) {
        // Получаем данные текущего чата
        const chatId = localStorage.getItem('current_chat_id');
        if (!chatId) {
          throw new Error('No active chat found');
        }
        
        const response = await fetch(`${API_URL}/api/chat-history/${chatId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch chat details');
        }
        
        const chatData = await response.json();
        
        // Находим сообщение бота
        const botMessage = chatData.messages.find((msg: any) => 
          msg.is_bot && msg.id.toString() === feedback.messageId
        );
        
        if (!botMessage) {
          throw new Error('Bot message not found');
        }
        
        // Обновляем метаданные сообщения с новым рейтингом
        const updatedMessageMetadata = {
          ...botMessage.message_metadata,
          feedback: feedback.type
        };
        
        // Отправляем запрос на обновление сообщения
        await fetch(`${API_URL}/api/chat-history/${feedback.messageId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          },
          body: JSON.stringify({
            message_metadata: updatedMessageMetadata
          }),
        });
      } else {
        // Используем имитацию ответа от API
        return new Promise(resolve => {
          setTimeout(() => {
            console.log('Feedback sent:', feedback);
            resolve();
          }, 300);
        });
      }
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  },
  
  /**
   * Завершает чат с оценкой
   * @param chatRating - Данные оценки чата
   */
  async finishChat(chatRating: ChatRatingRequest): Promise<void> {
    try {
      if (!USE_MOCK_API) {
        const chatId = localStorage.getItem('current_chat_id');
        if (!chatId) {
          throw new Error('No active chat found');
        }
        
        await fetch(`${API_URL}/api/chat-history/${chatId}/finish`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          },
          body: JSON.stringify(chatRating),
        });
        
        // Удаляем ID текущего чата из localStorage
        localStorage.removeItem('current_chat_id');
      } else {
        // Используем имитацию ответа от API
        return new Promise(resolve => {
          setTimeout(() => {
            console.log('Chat finished with rating:', chatRating);
            resolve();
          }, 300);
        });
      }
    } catch (error) {
      console.error('Error finishing chat:', error);
    }
  },
  
  /**
   * Имитация ответа бота на основе содержимого запроса
   * @param userInput - Сообщение пользователя
   * @returns Ответ бота
   */
  getMockResponse(userInput: string): string {
    const input = userInput.toLowerCase();
    
    if (input.includes('тендер') || input.includes('закупк')) {
      return 'Для участия в тендерах на Портале поставщиков вам необходимо зарегистрироваться и получить электронную подпись. После регистрации вы сможете просматривать доступные закупки и подавать заявки.';
    } else if (input.includes('регистрац')) {
      return 'Для регистрации на Портале поставщиков вам необходимо: 1) подготовить электронную подпись, 2) заполнить форму регистрации на сайте, 3) подтвердить данные компании. Подробную инструкцию вы можете найти в разделе "Помощь".';
    } else if (input.includes('оплат') || input.includes('цен')) {
      return 'Порядок оплаты по контракту устанавливается заказчиком в соответствии с 44-ФЗ. Обычно оплата производится в течение 15 рабочих дней с момента подписания акта выполненных работ.';
    } else if (input.includes('подпись') || input.includes('эцп')) {
      return 'Для работы на Портале поставщиков вам потребуется усиленная квалифицированная электронная подпись (УКЭП). Вы можете получить её в одном из аккредитованных удостоверяющих центров.';
    } else if (input.includes('документ') || input.includes('файл')) {
      return 'К заявке на участие в закупке необходимо приложить сканы всех требуемых документов в формате PDF. Размер каждого файла не должен превышать 20 МБ.';
    } else {
      return 'Спасибо за ваш вопрос. Для получения более подробной информации рекомендую обратиться к разделу FAQ на нашем портале или связаться со службой поддержки.';
    }
  },
  
  /**
   * Имитация получения источника информации
   * @param userInput - Сообщение пользователя
   * @returns Источник информации
   */
  getMockSource(userInput: string): string {
    const input = userInput.toLowerCase();
    
    if (input.includes('тендер') || input.includes('закупк')) {
      return 'Федеральный закон №44-ФЗ от 05.04.2013, статья 24';
    } else if (input.includes('регистрац')) {
      return 'Инструкция по регистрации на Портале поставщиков, раздел 2.1';
    } else if (input.includes('оплат') || input.includes('цен')) {
      return 'Федеральный закон №44-ФЗ от 05.04.2013, статья 34, часть 13.1';
    } else if (input.includes('подпись') || input.includes('эцп')) {
      return 'Федеральный закон №63-ФЗ от 06.04.2011 "Об электронной подписи"';
    } else if (input.includes('документ') || input.includes('файл')) {
      return 'Постановление Правительства РФ №1414 от 23.12.2015';
    } else {
      return 'База знаний Портала поставщиков';
    }
  }
};

export default chatService; 