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

// Базовый URL API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Сервис для работы с API чата
const chatService = {
  /**
   * Отправляет сообщение пользователя и получает ответ от бота
   * @param message - Сообщение пользователя
   * @returns Ответ от бота
   */
  async sendMessage(message: UserMessage): Promise<BotResponse> {
    try {
      // В реальном приложении здесь должен быть запрос к API
      // const response = await fetch(`${API_URL}/api/chat`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({ message: message.content }),
      // });
      // return await response.json();
      
      // Имитация ответа от API
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
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  /**
   * Получает историю чата пользователя
   * @returns Список элементов истории чата
   */
  async getChatHistory(): Promise<ChatHistoryItem[]> {
    try {
      // В реальном приложении здесь должен быть запрос к API
      // const response = await fetch(`${API_URL}/api/chat/history`, {
      //   method: 'GET',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      // });
      // return await response.json();
      
      // Имитация ответа от API
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
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  },

  /**
   * Отправляет обратную связь о сообщении бота
   * @param feedback - Данные обратной связи
   */
  async sendFeedback(feedback: FeedbackRequest): Promise<void> {
    try {
      // В реальном приложении здесь должен быть запрос к API
      // await fetch(`${API_URL}/api/chat/feedback`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify(feedback),
      // });
      
      // Имитация ответа от API
      return new Promise(resolve => {
        setTimeout(() => {
          console.log('Feedback sent:', feedback);
          resolve();
        }, 300);
      });
    } catch (error) {
      console.error('Error sending feedback:', error);
      throw error;
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