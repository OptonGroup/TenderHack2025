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
`;

const MainPage: React.FC = () => {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [historyItems, setHistoryItems] = useState<ChatHistoryItem[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

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
    // Здесь должна быть логика загрузки выбранного чата
    setIsHistoryOpen(false);
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

  return (
    <PageContainer>
      <Header 
        isLoggedIn={isLoggedIn} 
        userName={isLoggedIn ? "Александр Семенов" : undefined} 
        notificationCount={isLoggedIn ? 3 : 0} 
      />
      
      <MainContent>
        <ChatAssistant />
      </MainContent>
      
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