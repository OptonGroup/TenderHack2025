import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../../styles/theme.ts';

// Стили для управления чатами
const ChatsContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const ToolBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
`;

const SearchContainer = styled.div`
  flex: 1;
  max-width: 400px;
  position: relative;
  
  @media (max-width: 768px) {
    width: 100%;
    max-width: 100%;
  }
`;

const SearchInput = styled.input`
  width: 100%;
  height: 40px;
  padding: 0 16px 0 40px;
  font-size: 14px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  
  &:focus {
    border-color: ${colors.mainBlue};
    outline: none;
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  color: ${colors.paleBlack};
`;

const FiltersContainer = styled.div`
  display: flex;
  gap: 12px;
  
  @media (max-width: 768px) {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 8px;
    
    &::-webkit-scrollbar {
      height: 4px;
    }
    
    &::-webkit-scrollbar-track {
      background: ${colors.grayBlue};
      border-radius: 2px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: ${colors.mainBlue};
      border-radius: 2px;
    }
  }
`;

const FilterButton = styled.button<{ active?: boolean }>`
  padding: 8px 12px;
  background-color: ${props => props.active ? colors.mainBlue : colors.white};
  color: ${props => props.active ? colors.white : colors.black};
  border: 1px solid ${props => props.active ? colors.mainBlue : colors.grayBlue};
  border-radius: ${borderRadius.small};
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  
  &:hover {
    background-color: ${props => props.active ? colors.seaDark : colors.paleBlue};
  }
`;

const ChatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChatCard = styled.div`
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.medium};
  overflow: hidden;
  transition: all 0.2s ease;
  box-shadow: ${shadows.small};
  
  &:hover {
    box-shadow: ${shadows.medium};
    transform: translateY(-2px);
  }
`;

const ChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: ${colors.paleBlue};
  border-bottom: 1px solid ${colors.grayBlue};
`;

const ChatTitle = styled.div`
  font-weight: 500;
  font-size: 15px;
`;

const ChatDate = styled.div`
  color: ${colors.paleBlack};
  font-size: 12px;
`;

const ChatContent = styled.div`
  padding: 16px;
`;

const ChatUser = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: ${colors.grayBlue};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.white};
  font-size: 14px;
  font-weight: 500;
`;

const UserDetails = styled.div`
  margin-left: 12px;
`;

const UserName = styled.div`
  font-weight: 500;
  font-size: 14px;
`;

const UserEmail = styled.div`
  color: ${colors.paleBlack};
  font-size: 12px;
`;

const ChatStats = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  padding: 8px;
  background-color: ${colors.lightBg};
  border-radius: ${borderRadius.small};
`;

const StatValue = styled.div`
  font-weight: 500;
  font-size: 16px;
`;

const StatLabel = styled.div`
  color: ${colors.paleBlack};
  font-size: 12px;
`;

const ChatPreview = styled.div`
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  padding: 12px;
  font-size: 14px;
  max-height: 100px;
  overflow-y: auto;
  margin-bottom: 16px;
`;

const ChatFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ChatActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  border: none;
  background-color: ${colors.paleBlue};
  color: ${colors.paleBlack};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${colors.grayBlue};
    color: ${colors.black};
  }
`;

const Badge = styled.span<{ type: 'active' | 'completed' | 'flagged' }>`
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: ${borderRadius.small};
  font-size: 12px;
  font-weight: 500;
  
  background-color: ${props => {
    switch (props.type) {
      case 'active': return `${colors.success}20`;
      case 'completed': return `${colors.mainBlue}20`;
      case 'flagged': return `${colors.error}20`;
      default: return `${colors.mainBlue}20`;
    }
  }};
  
  color: ${props => {
    switch (props.type) {
      case 'active': return colors.success;
      case 'completed': return colors.mainBlue;
      case 'flagged': return colors.error;
      default: return colors.mainBlue;
    }
  }};
  
  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 4px;
    background-color: ${props => {
      switch (props.type) {
        case 'active': return colors.success;
        case 'completed': return colors.mainBlue;
        case 'flagged': return colors.error;
        default: return colors.mainBlue;
      }
    }};
  }
`;

const Pagination = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 36px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
  }
`;

const PaginationInfo = styled.div`
  font-size: 14px;
  color: ${colors.paleBlack};
  
  @media (max-width: 768px) {
    order: 2;
  }
`;

const PaginationControls = styled.div`
  display: flex;
  gap: 8px;
  
  @media (max-width: 768px) {
    order: 1;
    width: 100%;
    justify-content: center;
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
      <ChatsContainer>
        <div style={{ textAlign: 'center', padding: '32px' }}>
          Загрузка чатов...
        </div>
      </ChatsContainer>
    );
  }
  
  return (
    <ChatsContainer>
      <ToolBar>
        <SearchContainer>
          <SearchIcon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
            </svg>
          </SearchIcon>
          <SearchInput
            type="text"
            placeholder="Поиск чатов..."
            value={searchTerm}
            onChange={handleSearch}
          />
        </SearchContainer>
        
        <FiltersContainer>
          <FilterButton 
            active={statusFilter === 'all'}
            onClick={() => handleFilterChange('all')}
          >
            Все
          </FilterButton>
          <FilterButton 
            active={statusFilter === 'active'}
            onClick={() => handleFilterChange('active')}
          >
            Активные
          </FilterButton>
          <FilterButton 
            active={statusFilter === 'completed'}
            onClick={() => handleFilterChange('completed')}
          >
            Завершенные
          </FilterButton>
          <FilterButton 
            active={statusFilter === 'flagged'}
            onClick={() => handleFilterChange('flagged')}
          >
            Помеченные
          </FilterButton>
        </FiltersContainer>
      </ToolBar>
      
      {paginatedChats.length > 0 ? (
        <ChatsGrid>
          {paginatedChats.map(chat => (
            <ChatCard key={chat.id}>
              <ChatHeader>
                <ChatTitle>{chat.title}</ChatTitle>
                <Badge type={getStatusBadgeType(chat.status)}>
                  {getStatusText(chat.status)}
                </Badge>
              </ChatHeader>
              
              <ChatContent>
                <ChatUser>
                  <UserAvatar>{chat.user.name.charAt(0)}</UserAvatar>
                  <UserDetails>
                    <UserName>{chat.user.name}</UserName>
                    <UserEmail>{chat.user.email}</UserEmail>
                  </UserDetails>
                </ChatUser>
                
                <ChatStats>
                  <StatItem>
                    <StatValue>{chat.messagesCount}</StatValue>
                    <StatLabel>Сообщений</StatLabel>
                  </StatItem>
                  <StatItem>
                    <StatValue>{chat.queriesCount}</StatValue>
                    <StatLabel>Запросов</StatLabel>
                  </StatItem>
                </ChatStats>
                
                <ChatPreview>
                  {chat.lastMessage}
                </ChatPreview>
                
                <ChatFooter>
                  <ChatDate>{formatDate(chat.date)}</ChatDate>
                  <ChatActions>
                    <ActionButton title="Просмотреть" onClick={() => handleViewChat(chat.id)}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" fill="currentColor"/>
                      </svg>
                    </ActionButton>
                    <ActionButton 
                      title={chat.status === 'flagged' ? 'Снять отметку' : 'Отметить'} 
                      onClick={() => handleFlagChat(chat.id, chat.status)}
                    >
                      {chat.status === 'flagged' ? (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M14.43 10L12 2L9.57 10H2L8.18 14.41L5.83 22L12 17.31L18.18 22L15.83 14.41L22 10H14.43Z" fill="currentColor"/>
                        </svg>
                      ) : (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M22 9.24L14.81 8.62L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27L18.18 21L16.55 13.97L22 9.24ZM12 15.4L8.24 17.67L9.24 13.39L5.92 10.51L10.3 10.13L12 6.1L13.71 10.14L18.09 10.52L14.77 13.4L15.77 17.68L12 15.4Z" fill="currentColor"/>
                        </svg>
                      )}
                    </ActionButton>
                    <ActionButton title="Экспортировать" onClick={() => handleExportChat(chat.id)}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 9H15V3H9V9H5L12 16L19 9ZM5 18V20H19V18H5Z" fill="currentColor"/>
                      </svg>
                    </ActionButton>
                  </ChatActions>
                </ChatFooter>
              </ChatContent>
            </ChatCard>
          ))}
        </ChatsGrid>
      ) : (
        <div style={{ textAlign: 'center', padding: '32px' }}>
          Чаты не найдены
        </div>
      )}
      
      {paginatedChats.length > 0 && (
        <Pagination>
          <PaginationInfo>
            Показано {(currentPage - 1) * chatsPerPage + 1}-{Math.min(currentPage * chatsPerPage, filteredChats.length)} из {filteredChats.length} чатов
          </PaginationInfo>
          
          <PaginationControls>
            {renderPaginationButtons()}
          </PaginationControls>
        </Pagination>
      )}
    </ChatsContainer>
  );
};

export default ChatsManagement; 