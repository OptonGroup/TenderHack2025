import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../styles/theme.ts';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  height: 600px;
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.medium};
  margin: 32px auto;
  overflow: hidden;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  padding: 16px 24px;
  background-color: ${colors.paleBlue};
  border-bottom: 1px solid ${colors.grayBlue};
`;

const ChatTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: ${colors.black};
  margin: 0;
`;

const ChatMessages = styled.div`
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

interface MessageProps {
  isBot: boolean;
}

const MessageWrapper = styled.div<MessageProps>`
  display: flex;
  flex-direction: column;
  max-width: 80%;
  align-self: ${props => props.isBot ? 'flex-start' : 'flex-end'};
`;

const MessageContent = styled.div<MessageProps>`
  padding: 12px 16px;
  border-radius: ${borderRadius.medium};
  background-color: ${props => props.isBot ? colors.paleBlue : colors.mainBlue};
  color: ${props => props.isBot ? colors.black : colors.white};
  font-size: 14px;
  line-height: 1.5;
  box-shadow: ${shadows.small};
`;

const MessageSource = styled.div`
  margin-top: 8px;
  font-size: 12px;
  color: ${colors.paleBlack};
  
  a {
    color: ${colors.mainBlue};
    text-decoration: underline;
    margin-left: 8px;
    
    &:hover {
      color: ${colors.seaDark};
    }
  }
`;

const MessageFeedback = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
`;

const FeedbackButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: ${colors.gray};
  
  &:hover {
    color: ${colors.mainBlue};
  }
  
  &.active {
    color: ${colors.mainBlue};
  }
`;

const FeedbackText = styled.span`
  font-size: 12px;
  color: ${colors.paleBlack};
`;

const ChatInputContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid ${colors.grayBlue};
`;

const ChatInput = styled.input`
  flex: 1;
  height: 48px;
  padding: 0 16px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.medium};
  font-size: 14px;
  
  &:focus {
    border-color: ${colors.mainBlue};
    outline: none;
  }
`;

const SendButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  margin-left: 12px;
  background-color: ${colors.mainBlue};
  border: none;
  border-radius: ${borderRadius.small};
  color: white;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: ${colors.seaDark};
  }
  
  &:disabled {
    background-color: ${colors.grayBlue};
    cursor: not-allowed;
  }
`;

const HistoryButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  padding: 0 16px;
  margin-right: 12px;
  background-color: ${colors.paleBlue};
  border: none;
  border-radius: ${borderRadius.small};
  color: ${colors.black};
  font-size: 14px;
  cursor: pointer;
  
  &:hover {
    background-color: ${colors.grayBlue};
  }
`;

interface Message {
  id: string;
  content: string;
  isBot: boolean;
  source?: string;
  timestamp: Date;
  feedback?: 'positive' | 'negative' | null;
}

const ChatAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Здравствуйте! Я ИИ-ассистент Портала поставщиков. Чем я могу вам помочь?',
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isBot: false,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    // Имитация ответа от API
    setTimeout(() => {
      // Здесь должен быть запрос к API
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: getBotResponse(inputValue),
        isBot: true,
        source: 'Постановление Правительства №123 от 15.03.2022',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const getBotResponse = (userInput: string): string => {
    // Простая логика для имитации ответов
    if (userInput.toLowerCase().includes('тендер') || userInput.toLowerCase().includes('закупк')) {
      return 'Для участия в тендерах на Портале поставщиков вам необходимо зарегистрироваться и получить электронную подпись. После регистрации вы сможете просматривать доступные закупки и подавать заявки.';
    } else if (userInput.toLowerCase().includes('регистрац')) {
      return 'Для регистрации на Портале поставщиков вам необходимо: 1) подготовить электронную подпись, 2) заполнить форму регистрации на сайте, 3) подтвердить данные компании. Подробную инструкцию вы можете найти в разделе "Помощь".';
    } else if (userInput.toLowerCase().includes('оплат') || userInput.toLowerCase().includes('цен')) {
      return 'Порядок оплаты по контракту устанавливается заказчиком в соответствии с 44-ФЗ. Обычно оплата производится в течение 15 рабочих дней с момента подписания акта выполненных работ.';
    } else {
      return 'Спасибо за ваш вопрос. Для получения более подробной информации рекомендую обратиться к разделу FAQ на нашем портале или связаться со службой поддержки.';
    }
  };

  const handleFeedback = (messageId: string, type: 'positive' | 'negative') => {
    setMessages(prev => prev.map(message => {
      if (message.id === messageId) {
        return {
          ...message,
          feedback: message.feedback === type ? null : type
        };
      }
      return message;
    }));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>ИИ-ассистент Портала поставщиков</ChatTitle>
      </ChatHeader>
      
      <ChatMessages>
        {messages.map(message => (
          <MessageWrapper key={message.id} isBot={message.isBot}>
            <MessageContent isBot={message.isBot}>
              {message.content}
            </MessageContent>
            
            {message.isBot && message.source && (
              <MessageSource>
                Источник: <a href="#" target="_blank" rel="noopener noreferrer">{message.source}</a>
              </MessageSource>
            )}
            
            {message.isBot && (
              <MessageFeedback>
                <FeedbackButton 
                  className={message.feedback === 'positive' ? 'active' : ''}
                  onClick={() => handleFeedback(message.id, 'positive')}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 21H5V9H1V21ZM23 10C23 8.9 22.1 8 21 8H14.69L15.64 3.43L15.67 3.11C15.67 2.7 15.5 2.32 15.23 2.05L14.17 1L7.59 7.59C7.22 7.95 7 8.45 7 9V19C7 20.1 7.9 21 9 21H18C18.83 21 19.54 20.5 19.84 19.78L22.86 12.73C22.95 12.5 23 12.26 23 12V10Z" fill="currentColor"/>
                  </svg>
                </FeedbackButton>
                
                <FeedbackButton 
                  className={message.feedback === 'negative' ? 'active' : ''}
                  onClick={() => handleFeedback(message.id, 'negative')}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 3H6C5.17 3 4.46 3.5 4.16 4.22L1.14 11.27C1.05 11.5 1 11.74 1 12V14C1 15.1 1.9 16 3 16H9.31L8.36 20.57L8.33 20.89C8.33 21.3 8.5 21.68 8.77 21.95L9.83 23L16.41 16.41C16.78 16.05 17 15.55 17 15V5C17 3.9 16.1 3 15 3ZM23 3V15H19V3H23Z" fill="currentColor"/>
                  </svg>
                </FeedbackButton>
                
                <FeedbackText>
                  {message.feedback === 'positive' 
                    ? 'Спасибо за положительную оценку!' 
                    : message.feedback === 'negative' 
                    ? 'Спасибо за отзыв! Мы работаем над улучшением.' 
                    : 'Оцените ответ'}
                </FeedbackText>
              </MessageFeedback>
            )}
          </MessageWrapper>
        ))}
        <div ref={messagesEndRef} />
      </ChatMessages>
      
      <ChatInputContainer>
        <HistoryButton>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
            <path d="M13 3C8.03 3 4 7.03 4 12H1L4.89 15.89L4.96 16.03L9 12H6C6 8.13 9.13 5 13 5C16.87 5 20 8.13 20 12C20 15.87 16.87 19 13 19C11.07 19 9.32 18.21 8.06 16.94L6.64 18.36C8.27 19.99 10.51 21 13 21C17.97 21 22 16.97 22 12C22 7.03 17.97 3 13 3ZM12 8V13L16.28 15.54L17 14.33L13.5 12.25V8H12Z" fill="currentColor"/>
          </svg>
          История
        </HistoryButton>
        
        <ChatInput 
          type="text" 
          value={inputValue} 
          onChange={(e) => setInputValue(e.target.value)} 
          onKeyDown={handleKeyDown}
          placeholder="Введите ваш вопрос..."
          disabled={isLoading}
        />
        
        <SendButton onClick={handleSendMessage} disabled={inputValue.trim() === '' || isLoading}>
          {isLoading ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor"/>
              <path d="M12 4C7.59 4 4 7.59 4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <animateTransform 
                  attributeName="transform" 
                  type="rotate" 
                  from="0 12 12" 
                  to="360 12 12" 
                  dur="1s" 
                  repeatCount="indefinite" 
                />
              </path>
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
            </svg>
          )}
        </SendButton>
      </ChatInputContainer>
    </ChatContainer>
  );
};

export default ChatAssistant; 