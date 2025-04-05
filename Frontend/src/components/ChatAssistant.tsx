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
  
  @media (max-width: 768px) {
    margin: 16px auto;
    height: calc(100vh - 200px);
  }
  
  @media (max-width: 480px) {
    margin: 8px auto;
    height: calc(100vh - 160px);
    border-radius: ${borderRadius.small};
  }
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  padding: 16px 24px;
  background-color: ${colors.paleBlue};
  border-bottom: 1px solid ${colors.grayBlue};
  
  @media (max-width: 480px) {
    padding: 12px 16px;
  }
`;

const ChatTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: ${colors.black};
  margin: 0;
  
  @media (max-width: 480px) {
    font-size: 16px;
  }
`;

const ChatMessages = styled.div`
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  @media (max-width: 480px) {
    padding: 16px;
    gap: 12px;
  }
`;

interface MessageProps {
  isBot: boolean;
}

const MessageWrapper = styled.div<MessageProps>`
  display: flex;
  flex-direction: column;
  max-width: 80%;
  align-self: ${props => props.isBot ? 'flex-start' : 'flex-end'};
  
  @media (max-width: 480px) {
    max-width: 85%;
  }
`;

const MessageContent = styled.div<MessageProps>`
  padding: 12px 16px;
  border-radius: ${borderRadius.medium};
  background-color: ${props => props.isBot ? colors.paleBlue : colors.mainBlue};
  color: ${props => props.isBot ? colors.black : colors.white};
  font-size: 14px;
  line-height: 1.5;
  box-shadow: ${shadows.small};
  
  @media (max-width: 480px) {
    padding: 10px 12px;
    font-size: 13px;
  }
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
  
  @media (max-width: 480px) {
    font-size: 11px;
    margin-top: 6px;
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
  
  @media (max-width: 480px) {
    padding: 12px 16px;
  }
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
  
  @media (max-width: 480px) {
    height: 40px;
    padding: 0 12px;
    font-size: 13px;
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
  
  @media (max-width: 480px) {
    width: 40px;
    height: 40px;
    margin-left: 8px;
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
  
  @media (max-width: 480px) {
    height: 40px;
    padding: 0 12px;
    font-size: 13px;
    margin-right: 8px;
  }
`;

// Добавляем новые стили для кнопки "Завершить чат" и модальное окно оценки
const ActionButtons = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: auto;
  
  @media (max-width: 480px) {
    gap: 8px;
  }
`;

const FinishChatButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  padding: 0 16px;
  background-color: ${colors.orange};
  border: none;
  border-radius: ${borderRadius.small};
  color: white;
  font-size: 14px;
  cursor: pointer;
  
  &:hover {
    background-color: #e06010;
  }
  
  @media (max-width: 480px) {
    height: 40px;
    padding: 0 12px;
    font-size: 13px;
  }
`;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const RatingModal = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.medium};
  padding: 24px;
  width: 90%;
  max-width: 450px;
  text-align: center;
`;

const ModalTitle = styled.h3`
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 20px;
  color: ${colors.black};
`;

const StarsContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
`;

const Star = styled.button<{ filled: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  color: ${props => props.filled ? colors.orange : colors.grayBlue};
  font-size: 32px;
  transition: transform 0.2s, color 0.2s;
  
  &:hover {
    transform: scale(1.1);
    color: ${colors.orange};
  }
`;

const ModalButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
`;

const SubmitButton = styled.button`
  background-color: ${colors.mainBlue};
  color: white;
  border: none;
  border-radius: ${borderRadius.small};
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  
  &:hover {
    background-color: ${colors.seaDark};
  }
`;

const CancelButton = styled.button`
  background-color: ${colors.paleBlue};
  color: ${colors.black};
  border: none;
  border-radius: ${borderRadius.small};
  padding: 12px 24px;
  font-size: 16px;
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

interface ChatAssistantProps {
  onMessageSent?: (message: string, response: string) => void;
  onToggleHistory?: () => void;
  onRatingChange?: (messageId: string, rating: 'positive' | 'negative' | null) => void;
  onChatFinished?: (rating: number) => void;
  selectedChatId?: string | null;
}

const ChatAssistant: React.FC<ChatAssistantProps> = ({ 
  onMessageSent, 
  onToggleHistory,
  onRatingChange,
  onChatFinished,
  selectedChatId
}) => {
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
  // Добавляем новые состояния для модального окна оценки
  const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
  const [rating, setRating] = useState(0);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Загружаем сообщения выбранного чата из истории
  useEffect(() => {
    if (selectedChatId) {
      // В реальном приложении здесь должен быть запрос к API для загрузки полной истории чата
      // Сейчас просто имитируем загрузку сообщений
      const mockConversation: Message[] = [
        {
          id: `${selectedChatId}-1`,
          content: 'Здравствуйте! Я ИИ-ассистент Портала поставщиков. Чем я могу вам помочь?',
          isBot: true,
          timestamp: new Date(Date.now() - 3600000)
        },
        {
          id: `${selectedChatId}-2`,
          content: 'Как мне зарегистрироваться на портале?',
          isBot: false,
          timestamp: new Date(Date.now() - 3500000)
        },
        {
          id: `${selectedChatId}-3`,
          content: 'Для регистрации на Портале поставщиков вам необходимо: 1) подготовить электронную подпись, 2) заполнить форму регистрации на сайте, 3) подтвердить данные компании. Подробную инструкцию вы можете найти в разделе "Помощь".',
          isBot: true,
          source: 'Инструкция по регистрации на Портале поставщиков, раздел 2.1',
          timestamp: new Date(Date.now() - 3400000),
          feedback: null
        }
      ];
      
      setMessages(mockConversation);
    }
  }, [selectedChatId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage: UserMessage = { content: inputValue };
    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isBot: false,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      const response = await chatService.sendMessage(userMessage);
      
      const botMessage: Message = {
        id: response.id,
        content: response.content,
        isBot: true,
        source: response.source,
        timestamp: new Date(),
        feedback: null
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // Уведомляем родительский компонент о новом сообщении для истории
      if (onMessageSent) {
        onMessageSent(inputValue, response.content);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Извините, произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз позже.',
        isBot: true,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = (messageId: string, type: 'positive' | 'negative' | null) => {
    // Обновляем сообщение с обратной связью
    setMessages(prev => 
      prev.map(message => 
        message.id === messageId 
          ? { ...message, feedback: type } 
          : message
      )
    );
    
    // Уведомляем родительский компонент о смене рейтинга
    if (onRatingChange) {
      onRatingChange(messageId, type);
    }
  };

  const handleHistoryButtonClick = () => {
    if (onToggleHistory) {
      onToggleHistory();
    }
  };

  // Обработчик для кнопки "Завершить чат"
  const handleFinishChat = () => {
    setIsRatingModalOpen(true);
  };
  
  // Обработчик для выбора рейтинга
  const handleRatingSelect = (value: number) => {
    setRating(value);
  };
  
  // Обработчик для отправки рейтинга
  const handleRatingSubmit = () => {
    if (onChatFinished) {
      onChatFinished(rating);
    }
    setIsRatingModalOpen(false);
    
    // Очищаем историю сообщений после завершения чата
    setMessages([{
      id: new Date().getTime().toString(),
      content: 'Спасибо за оценку! Чем еще я могу вам помочь?',
      isBot: true,
      timestamp: new Date(),
    }]);
    setRating(0);
  };
  
  // Обработчик для отмены оценки
  const handleRatingCancel = () => {
    setIsRatingModalOpen(false);
    setRating(0);
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>Чат с ассистентом</ChatTitle>
        
        <HistoryButton onClick={handleHistoryButtonClick}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
            <path d="M13 3C8.03 3 4 7.03 4 12H1L4.89 15.89L4.96 16.03L9 12H6C6 8.13 9.13 5 13 5C16.87 5 20 8.13 20 12C20 15.87 16.87 19 13 19C11.07 19 9.32 18.21 8.06 16.94L6.64 18.36C8.27 19.99 10.51 21 13 21C17.97 21 22 16.97 22 12C22 7.03 17.97 3 13 3ZM12 8V13L16.28 15.54L17 14.33L13.5 12.25V8H12Z" fill="currentColor"/>
          </svg>
          История
        </HistoryButton>
      </ChatHeader>
      
      <ChatMessages>
        {messages.map(message => (
          <MessageWrapper key={message.id} isBot={message.isBot}>
            <MessageContent isBot={message.isBot}>
              {message.content}
            </MessageContent>
            
            {message.source && (
              <MessageSource>
                Источник: <a href="#">{message.source}</a>
              </MessageSource>
            )}
            
            {message.isBot && message.id !== '1' && (
              <MessageFeedback>
                <FeedbackButton 
                  className={message.feedback === 'positive' ? 'active' : ''} 
                  onClick={() => handleFeedback(message.id, message.feedback === 'positive' ? null : 'positive')}
                  aria-label="Положительная оценка"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 21H5V9H1V21ZM23 10C23 8.9 22.1 8 21 8H14.69L15.64 3.43L15.67 3.11C15.67 2.7 15.5 2.32 15.23 2.05L14.17 1L7.59 7.59C7.22 7.95 7 8.45 7 9V19C7 20.1 7.9 21 9 21H18C18.83 21 19.54 20.5 19.84 19.78L22.86 12.73C22.95 12.5 23 12.26 23 12V10Z" fill="currentColor"/>
                  </svg>
                </FeedbackButton>
                
                <FeedbackButton 
                  className={message.feedback === 'negative' ? 'active' : ''} 
                  onClick={() => handleFeedback(message.id, message.feedback === 'negative' ? null : 'negative')}
                  aria-label="Отрицательная оценка"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 3H6C5.17 3 4.46 3.5 4.16 4.22L1.14 11.27C1.05 11.5 1 11.74 1 12V14C1 15.1 1.9 16 3 16H9.31L8.36 20.57L8.33 20.89C8.33 21.3 8.5 21.68 8.77 21.95L9.83 23L16.41 16.41C16.78 16.05 17 15.55 17 15V5C17 3.9 16.1 3 15 3ZM23 3V15H19V3H23Z" fill="currentColor"/>
                  </svg>
                </FeedbackButton>
                
                <FeedbackText>
                  {message.feedback === 'positive' && 'Спасибо за положительную оценку!'}
                  {message.feedback === 'negative' && 'Спасибо за отзыв. Мы постараемся улучшить ответы.'}
                </FeedbackText>
              </MessageFeedback>
            )}
          </MessageWrapper>
        ))}
        
        {isLoading && (
          <MessageWrapper isBot={true}>
            <MessageContent isBot={true}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ marginRight: '8px' }}>Печатает</span>
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#000', margin: '0 2px', animation: 'pulse 1s infinite' }}></span>
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#000', margin: '0 2px', animation: 'pulse 1s infinite .2s' }}></span>
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#000', margin: '0 2px', animation: 'pulse 1s infinite .4s' }}></span>
              </div>
            </MessageContent>
          </MessageWrapper>
        )}
        
        <div ref={messagesEndRef} />
      </ChatMessages>
      
      <ChatInputContainer>
        <ActionButtons>
          <HistoryButton onClick={handleHistoryButtonClick}>
            История
          </HistoryButton>
          <FinishChatButton onClick={handleFinishChat}>
            Завершить чат
          </FinishChatButton>
        </ActionButtons>
        <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%' }}>
          <ChatInput 
            type="text" 
            placeholder="Введите ваш вопрос..." 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
          />
          
          <SendButton type="submit" disabled={!inputValue.trim() || isLoading}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
            </svg>
          </SendButton>
        </form>
      </ChatInputContainer>
      
      {/* Модальное окно для оценки */}
      {isRatingModalOpen && (
        <ModalOverlay>
          <RatingModal>
            <ModalTitle>Оцените качество обслуживания</ModalTitle>
            <StarsContainer>
              {[1, 2, 3, 4, 5].map((star) => (
                <Star 
                  key={star} 
                  filled={star <= rating}
                  onClick={() => handleRatingSelect(star)}
                >
                  {star <= rating 
                    ? <span>★</span>
                    : <span>☆</span>
                  }
                </Star>
              ))}
            </StarsContainer>
            <ModalButtons>
              <CancelButton onClick={handleRatingCancel}>Отмена</CancelButton>
              <SubmitButton onClick={handleRatingSubmit} disabled={rating === 0}>Отправить</SubmitButton>
            </ModalButtons>
          </RatingModal>
        </ModalOverlay>
      )}
    </ChatContainer>
  );
};

ChatAssistant.defaultProps = {
  onMessageSent: undefined,
  onToggleHistory: undefined,
  onRatingChange: undefined,
  onChatFinished: undefined,
  selectedChatId: null
};

export default ChatAssistant; 