import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Header from '../components/Header.tsx';
import Footer from '../components/Footer.tsx';
import ChatAssistant from '../components/ChatAssistant.tsx';
import ChatHistory from '../components/ChatHistory.tsx';
import chatService, { ChatHistoryItem } from '../api/chatService.ts';
import { colors } from '../styles/theme.ts';

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${colors.lightBg};
`;

const MainContent = styled.main`
  flex: 1;
  padding: 24px 0;
  
  @media (max-width: 768px) {
    padding: 16px 0;
  }
  
  @media (max-width: 480px) {
    padding: 8px 0;
  }
`;

// Добавляем компонент для перекрытия контента при открытом меню истории на мобильных устройствах
const Overlay = styled.div<{ isVisible: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: ${props => props.isVisible ? 'block' : 'none'};
  
  @media (min-width: 481px) {
    display: none;
  }
`;

const MainPage: React.FC = () => {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [historyItems, setHistoryItems] = useState<ChatHistoryItem[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);

  useEffect(() => {
    // Имитация проверки авторизации
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
    
    // Загрузка истории чата, если пользователь авторизован
    if (token) {
      loadChatHistory();
    }
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await chatService.getChatHistory();
      setHistoryItems(history);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const toggleHistory = () => {
    setIsHistoryOpen(prev => !prev);
  };

  const selectChat = (chatId: string) => {
    console.log('Selected chat:', chatId);
    setSelectedChatId(chatId);
    // Здесь должна быть логика загрузки выбранного чата
    // Находим чат по ID и загружаем его содержимое
    const selectedChat = historyItems.find(item => item.id === chatId);
    if (selectedChat) {
      // Можно добавить дополнительную логику загрузки полной истории чата
      console.log('Загружен чат:', selectedChat);
    }
    setIsHistoryOpen(false);
  };

  const handleNewMessageSent = (message: string, response: string) => {
    // Добавляем новый элемент в историю чатов
    const newHistoryItem: ChatHistoryItem = {
      id: Date.now().toString(),
      question: message,
      answer: response,
      date: new Date().toISOString(),
      rating: null
    };
    
    setHistoryItems(prev => [newHistoryItem, ...prev]);
  };

  const handleRatingChange = (chatId: string, rating: 'positive' | 'negative' | null) => {
    // Обновляем рейтинг чата в истории
    setHistoryItems(prev => 
      prev.map(item => 
        item.id === chatId 
          ? { ...item, rating } 
          : item
      )
    );
    
    // Здесь можно отправить рейтинг на сервер
    chatService.sendFeedback({ messageId: chatId, type: rating })
      .catch(error => console.error('Failed to send feedback:', error));
  };

  const handleLogin = () => {
    // Имитация входа в систему
    localStorage.setItem('token', 'mock-token');
    setIsLoggedIn(true);
    loadChatHistory();
  };

  const handleLogout = () => {
    // Имитация выхода из системы
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setHistoryItems([]);
  };

  // Добавляем функцию для закрытия истории при клике по оверлею
  const closeHistory = () => {
    setIsHistoryOpen(false);
  };

  return (
    <PageContainer>
      <Header 
        isLoggedIn={isLoggedIn} 
        userName={isLoggedIn ? "Александр Семенов" : undefined} 
        notificationCount={isLoggedIn ? 3 : 0} 
      />
      
      <MainContent>
        <ChatAssistant 
          onMessageSent={handleNewMessageSent}
          onToggleHistory={toggleHistory}
          onRatingChange={handleRatingChange}
          selectedChatId={selectedChatId}
        />
      </MainContent>
      
      {/* Оверлей для закрытия истории на мобильных устройствах */}
      <Overlay isVisible={isHistoryOpen} onClick={closeHistory} />
      
      <ChatHistory 
        isOpen={isHistoryOpen} 
        onClose={toggleHistory} 
        onSelectChat={selectChat} 
        historyItems={historyItems} 
      />
      
      <Footer />
    </PageContainer>
  );
};

export default MainPage; 