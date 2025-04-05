import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../../styles/theme.ts';

// Стили для управления чатами
const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Card = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h2`
  font-size: 20px;
  margin: 0;
`;

const Button = styled.button`
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #303f9f;
  }
`;

const ChatList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ChatItem = styled.div`
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: box-shadow 0.2s;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 16px;
  margin-right: 16px;
  flex-shrink: 0;
`;

const ChatInfo = styled.div`
  flex: 1;
`;

const ChatTitle = styled.div`
  font-weight: 500;
  margin-bottom: 4px;
`;

const LastMessage = styled.div`
  font-size: 14px;
  color: #6c757d;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ChatTime = styled.div`
  font-size: 12px;
  color: #6c757d;
  margin-left: 16px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #3f51b5;
  cursor: pointer;
  margin-left: 16px;
  
  &:hover {
    text-decoration: underline;
  }
`;

const PageButton = styled.button<{ active?: boolean }>`
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  border: 1px solid ${props => props.active ? colors.mainBlue : colors.grayBlue};
  background-color: ${props => props.active ? colors.mainBlue : 'transparent'};
  color: ${props => props.active ? colors.white : colors.black};
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: ${colors.mainBlue};
    background-color: ${props => props.active ? colors.mainBlue : colors.paleBlue};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// Типы данных
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface Chat {
  id: string;
  title: string;
  user: User;
  status: 'active' | 'completed' | 'flagged';
  date: Date;
  messagesCount: number;
  queriesCount: number;
  lastMessage: string;
}

// Компонент управления чатами
const ChatsManagement: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed' | 'flagged'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  
  const chatsPerPage = 6;
  
  // Загрузка данных
  useEffect(() => {
    const fetchChats = async () => {
      setLoading(true);
      
      try {
        // Имитация запроса к API
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Примеры сообщений для предпросмотра
        const exampleMessages = [
          'Здравствуйте, чем я могу вам помочь?',
          'Подскажите, какие документы нужны для оформления заявки?',
          'Хотел бы получить консультацию по вопросу тендерной документации.',
          'Когда будут известны результаты рассмотрения заявок?',
          'Не могу загрузить файл, выдаёт ошибку.',
          'Как мне поменять контактные данные в профиле?'
        ];
        
        // Генерация моковых данных
        const mockChats = Array.from({ length: 20 }, (_, index) => ({
          id: `chat${index + 1}`,
          title: `Обращение #${Math.floor(Math.random() * 1000) + 1000}`,
          user: {
            id: `user${index % 10 + 1}`,
            name: `Пользователь ${index % 10 + 1}`,
            email: `user${index % 10 + 1}@example.com`
          },
          status: ['active', 'completed', 'flagged'][Math.floor(Math.random() * 3)] as 'active' | 'completed' | 'flagged',
          date: new Date(Date.now() - Math.random() * 10000000000),
          messagesCount: Math.floor(Math.random() * 25) + 5,
          queriesCount: Math.floor(Math.random() * 10) + 1,
          lastMessage: exampleMessages[Math.floor(Math.random() * exampleMessages.length)]
        }));
        
        setChats(mockChats);
        setTotalPages(Math.ceil(mockChats.length / chatsPerPage));
      } catch (error) {
        console.error('Ошибка при загрузке чатов:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchChats();
  }, []);
  
  // Фильтрация чатов
  const filteredChats = chats.filter(chat => {
    // Фильтр по поиску
    const searchMatch = 
      chat.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chat.user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chat.user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chat.lastMessage.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Фильтр по статусу
    const statusMatch = statusFilter === 'all' || chat.status === statusFilter;
    
    return searchMatch && statusMatch;
  });
  
  // Пагинация
  const paginatedChats = filteredChats.slice(
    (currentPage - 1) * chatsPerPage,
    currentPage * chatsPerPage
  );
  
  // Обработчики событий
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Сбрасываем страницу при поиске
  };
  
  const handleFilterChange = (status: 'all' | 'active' | 'completed' | 'flagged') => {
    setStatusFilter(status);
    setCurrentPage(1); // Сбрасываем страницу при смене фильтра
  };
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  
  const handleViewChat = (chatId: string) => {
    console.log(`Просмотр чата с ID: ${chatId}`);
    // Здесь будет логика перехода к просмотру чата
  };
  
  const handleFlagChat = (chatId: string, currentStatus: string) => {
    console.log(`${currentStatus === 'flagged' ? 'Снятие отметки' : 'Отметка'} чата с ID: ${chatId}`);
    
    // Имитация изменения статуса чата
    setChats(prevChats => 
      prevChats.map(chat => 
        chat.id === chatId 
          ? { 
              ...chat, 
              status: chat.status === 'flagged' ? 'active' : 'flagged' 
            } 
          : chat
      )
    );
  };
  
  const handleExportChat = (chatId: string) => {
    console.log(`Экспорт чата с ID: ${chatId}`);
    // Здесь будет логика экспорта чата
  };
  
  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(date);
  };
  
  // Создание кнопок пагинации
  const renderPaginationButtons = () => {
    const buttons = [];
    
    // Кнопка "Предыдущая"
    buttons.push(
      <PageButton 
        key="prev" 
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15.41 7.41L14 6L8 12L14 18L15.41 16.59L10.83 12L15.41 7.41Z" fill="currentColor"/>
        </svg>
      </PageButton>
    );
    
    // Первая страница
    if (currentPage > 2) {
      buttons.push(
        <PageButton 
          key={1} 
          onClick={() => handlePageChange(1)}
          active={currentPage === 1}
        >
          1
        </PageButton>
      );
    }
    
    // Многоточие в начале
    if (currentPage > 3) {
      buttons.push(
        <PageButton key="ellipsis1" disabled>...</PageButton>
      );
    }
    
    // Текущая страница и соседние
    for (let i = Math.max(1, currentPage - 1); i <= Math.min(totalPages, currentPage + 1); i++) {
      buttons.push(
        <PageButton 
          key={i} 
          onClick={() => handlePageChange(i)}
          active={currentPage === i}
        >
          {i}
        </PageButton>
      );
    }
    
    // Многоточие в конце
    if (currentPage < totalPages - 2) {
      buttons.push(
        <PageButton key="ellipsis2" disabled>...</PageButton>
      );
    }
    
    // Последняя страница
    if (currentPage < totalPages - 1 && totalPages > 1) {
      buttons.push(
        <PageButton 
          key={totalPages} 
          onClick={() => handlePageChange(totalPages)}
          active={currentPage === totalPages}
        >
          {totalPages}
        </PageButton>
      );
    }
    
    // Кнопка "Следующая"
    buttons.push(
      <PageButton 
        key="next" 
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8.59 16.59L10 18L16 12L10 6L8.59 7.41L13.17 12L8.59 16.59Z" fill="currentColor"/>
        </svg>
      </PageButton>
    );
    
    return buttons;
  };
  
  const getStatusBadgeType = (status: string): 'active' | 'completed' | 'flagged' => {
    switch (status) {
      case 'active': return 'active';
      case 'completed': return 'completed';
      case 'flagged': return 'flagged';
      default: return 'completed';
    }
  };
  
  const getStatusText = (status: string): string => {
    switch (status) {
      case 'active': return 'Активен';
      case 'completed': return 'Завершен';
      case 'flagged': return 'Помечен';
      default: return 'Неизвестно';
    }
  };
  
  if (loading) {
    return (
      <Container>
        <div style={{ textAlign: 'center', padding: '32px' }}>
          Загрузка чатов...
        </div>
      </Container>
    );
  }
  
  return (
    <Container>
      <Card>
        <Header>
          <Title>Управление чатами</Title>
          <Button>Экспорт истории</Button>
        </Header>
        
        <ChatList>
          {paginatedChats.map(chat => (
            <ChatItem key={chat.id}>
              <Avatar>{chat.user.name.charAt(0)}</Avatar>
              <ChatInfo>
                <ChatTitle>{chat.user.name}</ChatTitle>
                <LastMessage>{chat.lastMessage}</LastMessage>
              </ChatInfo>
              <ChatTime>{formatDate(chat.date)}</ChatTime>
              <ActionButton>Открыть</ActionButton>
              <ActionButton>Архивировать</ActionButton>
            </ChatItem>
          ))}
        </ChatList>
      </Card>
    </Container>
  );
};

export default ChatsManagement; 