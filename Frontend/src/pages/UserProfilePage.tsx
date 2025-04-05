import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../styles/theme.ts';
import Header from '../components/Header.tsx';
import Footer from '../components/Footer.tsx';

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${colors.lightBg};
`;

const MainContent = styled.main`
  flex: 1;
  padding: 32px 0;
  
  @media (max-width: 768px) {
    padding: 16px 0;
  }
`;

const Container = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
`;

const ProfileHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
`;

const ProfileTitle = styled.h1`
  font-size: 28px;
  font-weight: 600;
  color: ${colors.black};
  
  @media (max-width: 768px) {
    font-size: 24px;
  }
`;

const ProfileActions = styled.div`
  display: flex;
  gap: 16px;
  
  @media (max-width: 480px) {
    width: 100%;
    flex-direction: column;
  }
`;

const Button = styled.button`
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border-radius: ${borderRadius.small};
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
`;

const PrimaryButton = styled(Button)`
  background-color: ${colors.mainBlue};
  color: white;
  
  &:hover {
    background-color: ${colors.seaDark};
  }
`;

const SecondaryButton = styled(Button)`
  background-color: ${colors.white};
  color: ${colors.black};
  border: 1px solid ${colors.grayBlue};
  
  &:hover {
    background-color: ${colors.paleBlue};
  }
`;

const TabsContainer = styled.div`
  display: flex;
  margin-bottom: 24px;
  border-bottom: 1px solid ${colors.grayBlue};
  
  @media (max-width: 480px) {
    overflow-x: auto;
    white-space: nowrap;
    
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

const Tab = styled.button<{ active: boolean }>`
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  color: ${props => props.active ? colors.mainBlue : colors.paleBlack};
  background: none;
  border: none;
  border-bottom: 2px solid ${props => props.active ? colors.mainBlue : 'transparent'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    color: ${colors.mainBlue};
  }
  
  @media (max-width: 768px) {
    padding: 10px 16px;
    font-size: 14px;
  }
`;

const ContentContainer = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.small};
  padding: 24px;
  
  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const ProfileSection = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ProfileCard = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.small};
  padding: 24px;
  
  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const Avatar = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: ${colors.grayBlue};
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.white};
  font-size: 48px;
  font-weight: 500;
  
  @media (max-width: 768px) {
    width: 80px;
    height: 80px;
    font-size: 32px;
  }
`;

const ProfileInfo = styled.div`
  text-align: center;
`;

const ProfileName = styled.h2`
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 8px;
`;

const ProfileDetail = styled.p`
  color: ${colors.paleBlack};
  margin-bottom: 8px;
  font-size: 14px;
`;

const ProfileStats = styled.div`
  display: flex;
  justify-content: space-around;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid ${colors.grayBlue};
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 20px;
  font-weight: 600;
  color: ${colors.mainBlue};
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: ${colors.paleBlack};
`;

// Компоненты для вкладки Чаты
const ChatList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ChatItem = styled.div`
  display: flex;
  padding: 16px;
  border-radius: ${borderRadius.small};
  border: 1px solid ${colors.grayBlue};
  transition: all 0.2s ease;
  cursor: pointer;
  
  &:hover {
    border-color: ${colors.mainBlue};
    box-shadow: ${shadows.small};
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 12px;
  }
`;

const ChatInfo = styled.div`
  flex: 1;
`;

const ChatTitle = styled.h3`
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
`;

const ChatPreview = styled.p`
  font-size: 14px;
  color: ${colors.paleBlack};
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ChatMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: ${colors.paleBlack};
`;

interface StatusProps {
  status: 'resolved' | 'in-progress' | 'pending' | 'reopened';
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'resolved': return colors.success;
    case 'in-progress': return colors.mainBlue;
    case 'pending': return colors.warning;
    case 'reopened': return colors.error;
    default: return colors.paleBlack;
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'resolved': return 'Решено';
    case 'in-progress': return 'В процессе';
    case 'pending': return 'Требует ответа';
    case 'reopened': return 'Переоткрыто';
    default: return 'Неизвестно';
  }
};

const ChatStatus = styled.span<StatusProps>`
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: ${borderRadius.small};
  background-color: ${props => getStatusColor(props.status)}20;
  color: ${props => getStatusColor(props.status)};
  font-size: 12px;
  font-weight: 500;
  
  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: ${props => getStatusColor(props.status)};
    margin-right: 6px;
  }
`;

const ChatActions = styled.div`
  display: flex;
  gap: 16px;
  align-items: center;
  
  @media (max-width: 768px) {
    justify-content: flex-end;
    width: 100%;
  }
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
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

// Компоненты для архива
const SearchContainer = styled.div`
  margin-bottom: 24px;
`;

const SearchInput = styled.input`
  width: 100%;
  height: 48px;
  padding: 0 16px;
  font-size: 14px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  
  &:focus {
    border-color: ${colors.mainBlue};
    outline: none;
  }
`;

const FilterContainer = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
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
  
  @media (max-width: 768px) {
    flex-wrap: nowrap;
  }
`;

const FilterButton = styled.button<{ active: boolean }>`
  padding: 8px 16px;
  background-color: ${props => props.active ? colors.mainBlue : colors.white};
  color: ${props => props.active ? colors.white : colors.black};
  border: 1px solid ${props => props.active ? colors.mainBlue : colors.grayBlue};
  border-radius: ${borderRadius.small};
  font-size: 14px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.active ? colors.seaDark : colors.paleBlue};
  }
  
  @media (max-width: 768px) {
    flex-shrink: 0;
  }
`;

// Типы данных
interface User {
  id: string;
  name: string;
  email: string;
  organization: string;
  joinDate: Date;
}

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  status: 'resolved' | 'in-progress' | 'pending' | 'reopened';
  date: Date;
  unread?: number;
}

// Страница профиля пользователя
const UserProfilePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'active-chats' | 'archive'>('profile');
  const [user, setUser] = useState<User | null>(null);
  const [activeChats, setActiveChats] = useState<Chat[]>([]);
  const [archivedChats, setArchivedChats] = useState<Chat[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  
  useEffect(() => {
    // Загружаем данные пользователя из localStorage (имитация получения с сервера)
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const userData = JSON.parse(storedUser);
      setUser({
        id: userData.id || '1',
        name: userData.name || 'Александр Семенов',
        email: userData.email || 'user@example.com',
        organization: 'ООО "Технологии Будущего"',
        joinDate: new Date(2023, 0, 15)
      });
    }
    
    // Имитация загрузки данных с сервера
    loadMockData();
  }, []);
  
  const loadMockData = () => {
    // Имитация активных чатов
    setActiveChats([
      {
        id: '1',
        title: 'Вопрос по регистрации на тендер',
        lastMessage: 'Для регистрации на тендер вам необходимо предоставить следующие документы...',
        status: 'in-progress',
        date: new Date(Date.now() - 1000 * 60 * 60 * 2),
        unread: 1
      },
      {
        id: '2',
        title: 'Проблема с загрузкой документов',
        lastMessage: 'Пожалуйста, убедитесь, что размер файла не превышает 10 МБ и формат соответствует требуемому...',
        status: 'pending',
        date: new Date(Date.now() - 1000 * 60 * 60 * 24),
      }
    ]);
    
    // Имитация архивных чатов
    setArchivedChats([
      {
        id: '3',
        title: 'Вопрос по оплате контракта',
        lastMessage: 'Оплата по контракту будет произведена в течение 15 рабочих дней после подписания акта...',
        status: 'resolved',
        date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5)
      },
      {
        id: '4',
        title: 'Консультация по электронной подписи',
        lastMessage: 'Для работы с системой вам потребуется усиленная квалифицированная электронная подпись...',
        status: 'resolved',
        date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10)
      },
      {
        id: '5',
        title: 'Проблема с авторизацией',
        lastMessage: 'Проблема была связана с временными техническими работами. Сейчас система функционирует в штатном режиме...',
        status: 'reopened',
        date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15)
      }
    ]);
  };
  
  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  const filteredArchivedChats = archivedChats
    .filter(chat => {
      // Применяем поиск
      if (searchTerm && !chat.title.toLowerCase().includes(searchTerm.toLowerCase()) && 
          !chat.lastMessage.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      
      // Применяем фильтр по статусу
      if (activeFilter !== 'all' && chat.status !== activeFilter) {
        return false;
      }
      
      return true;
    })
    .sort((a, b) => b.date.getTime() - a.date.getTime()); // Сортировка по дате (сначала новые)
  
  const handleExportChat = (chatId: string) => {
    console.log(`Экспорт чата с ID: ${chatId}`);
    // Здесь будет логика экспорта чата
    alert('Чат экспортирован в PDF');
  };
  
  const handleReopenChat = (chatId: string) => {
    console.log(`Повторное открытие чата с ID: ${chatId}`);
    // Здесь будет логика переоткрытия чата
    setArchivedChats(prev => 
      prev.map(chat => 
        chat.id === chatId ? { ...chat, status: 'reopened' as 'reopened' } : chat
      )
    );
    
    // Добавляем чат в активные
    const chatToReopen = archivedChats.find(chat => chat.id === chatId);
    if (chatToReopen) {
      setActiveChats(prev => [...prev, { ...chatToReopen, date: new Date() }]);
    }
  };
  
  return (
    <PageContainer>
      <Header 
        isLoggedIn={true} 
        userName={user?.name} 
        notificationCount={activeChats.reduce((count, chat) => count + (chat.unread || 0), 0)}
      />
      
      <MainContent>
        <Container>
          <ProfileHeader>
            <ProfileTitle>Личный кабинет</ProfileTitle>
            <ProfileActions>
              <SecondaryButton>Настройки профиля</SecondaryButton>
              <PrimaryButton>Новый запрос</PrimaryButton>
            </ProfileActions>
          </ProfileHeader>
          
          <TabsContainer>
            <Tab 
              active={activeTab === 'profile'} 
              onClick={() => setActiveTab('profile')}
            >
              Профиль
            </Tab>
            <Tab 
              active={activeTab === 'active-chats'} 
              onClick={() => setActiveTab('active-chats')}
            >
              Активные чаты {activeChats.length > 0 && `(${activeChats.length})`}
            </Tab>
            <Tab 
              active={activeTab === 'archive'} 
              onClick={() => setActiveTab('archive')}
            >
              Архив запросов
            </Tab>
          </TabsContainer>
          
          {activeTab === 'profile' && (
            <ProfileSection>
              <ProfileCard>
                <Avatar>{user?.name.charAt(0)}</Avatar>
                <ProfileInfo>
                  <ProfileName>{user?.name}</ProfileName>
                  <ProfileDetail>{user?.email}</ProfileDetail>
                  <ProfileDetail>{user?.organization}</ProfileDetail>
                  <ProfileDetail>На портале с {user?.joinDate.toLocaleDateString('ru-RU')}</ProfileDetail>
                </ProfileInfo>
                <ProfileStats>
                  <StatItem>
                    <StatValue>{activeChats.length}</StatValue>
                    <StatLabel>Активные чаты</StatLabel>
                  </StatItem>
                  <StatItem>
                    <StatValue>{archivedChats.length}</StatValue>
                    <StatLabel>Архивные запросы</StatLabel>
                  </StatItem>
                </ProfileStats>
              </ProfileCard>
              
              <ContentContainer>
                <h2 style={{ marginBottom: '20px' }}>Недавняя активность</h2>
                <ChatList>
                  {[...activeChats].sort((a, b) => b.date.getTime() - a.date.getTime()).slice(0, 3).map(chat => (
                    <ChatItem key={chat.id}>
                      <ChatInfo>
                        <ChatTitle>{chat.title}</ChatTitle>
                        <ChatPreview>{chat.lastMessage}</ChatPreview>
                        <ChatMeta>
                          <ChatStatus status={chat.status}>{getStatusText(chat.status)}</ChatStatus>
                          <span>{formatDate(chat.date)}</span>
                        </ChatMeta>
                      </ChatInfo>
                    </ChatItem>
                  ))}
                </ChatList>
              </ContentContainer>
            </ProfileSection>
          )}
          
          {activeTab === 'active-chats' && (
            <ContentContainer>
              <h2 style={{ marginBottom: '20px' }}>Активные чаты</h2>
              
              {activeChats.length > 0 ? (
                <ChatList>
                  {activeChats.map(chat => (
                    <ChatItem key={chat.id}>
                      <ChatInfo>
                        <ChatTitle>
                          {chat.title}
                          {chat.unread && chat.unread > 0 && (
                            <span style={{ 
                              marginLeft: '8px', 
                              backgroundColor: colors.red, 
                              color: 'white', 
                              borderRadius: '50%', 
                              padding: '2px 6px',
                              fontSize: '12px'
                            }}>
                              {chat.unread}
                            </span>
                          )}
                        </ChatTitle>
                        <ChatPreview>{chat.lastMessage}</ChatPreview>
                        <ChatMeta>
                          <ChatStatus status={chat.status}>{getStatusText(chat.status)}</ChatStatus>
                          <span>{formatDate(chat.date)}</span>
                        </ChatMeta>
                      </ChatInfo>
                      <ChatActions>
                        <ActionButton title="Продолжить чат">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H6L4 18V4H20V16Z" fill="currentColor"/>
                          </svg>
                        </ActionButton>
                        <ActionButton title="Экспортировать" onClick={() => handleExportChat(chat.id)}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 9H15V3H9V9H5L12 16L19 9ZM5 18V20H19V18H5Z" fill="currentColor"/>
                          </svg>
                        </ActionButton>
                      </ChatActions>
                    </ChatItem>
                  ))}
                </ChatList>
              ) : (
                <div style={{ textAlign: 'center', padding: '32px', color: colors.paleBlack }}>
                  <p>У вас нет активных чатов</p>
                  <PrimaryButton style={{ marginTop: '16px' }}>Создать новый запрос</PrimaryButton>
                </div>
              )}
            </ContentContainer>
          )}
          
          {activeTab === 'archive' && (
            <ContentContainer>
              <h2 style={{ marginBottom: '20px' }}>Архив запросов</h2>
              
              <SearchContainer>
                <SearchInput 
                  type="text" 
                  placeholder="Поиск по архиву" 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </SearchContainer>
              
              <FilterContainer>
                <FilterButton 
                  active={activeFilter === 'all'}
                  onClick={() => setActiveFilter('all')}
                >
                  Все
                </FilterButton>
                <FilterButton 
                  active={activeFilter === 'resolved'}
                  onClick={() => setActiveFilter('resolved')}
                >
                  Решено
                </FilterButton>
                <FilterButton 
                  active={activeFilter === 'in-progress'}
                  onClick={() => setActiveFilter('in-progress')}
                >
                  В процессе
                </FilterButton>
                <FilterButton 
                  active={activeFilter === 'pending'}
                  onClick={() => setActiveFilter('pending')}
                >
                  Требует ответа
                </FilterButton>
                <FilterButton 
                  active={activeFilter === 'reopened'}
                  onClick={() => setActiveFilter('reopened')}
                >
                  Переоткрыто
                </FilterButton>
              </FilterContainer>
              
              {filteredArchivedChats.length > 0 ? (
                <ChatList>
                  {filteredArchivedChats.map(chat => (
                    <ChatItem key={chat.id}>
                      <ChatInfo>
                        <ChatTitle>{chat.title}</ChatTitle>
                        <ChatPreview>{chat.lastMessage}</ChatPreview>
                        <ChatMeta>
                          <ChatStatus status={chat.status}>{getStatusText(chat.status)}</ChatStatus>
                          <span>{formatDate(chat.date)}</span>
                        </ChatMeta>
                      </ChatInfo>
                      <ChatActions>
                        <ActionButton title="Просмотреть">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" fill="currentColor"/>
                          </svg>
                        </ActionButton>
                        <ActionButton title="Переоткрыть" onClick={() => handleReopenChat(chat.id)}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4C7.58 4 4 7.58 4 12C4 16.42 7.58 20 12 20C15.73 20 18.84 17.45 19.73 14H17.65C16.83 16.33 14.61 18 12 18C8.69 18 6 15.31 6 12C6 8.69 8.69 6 12 6C13.66 6 15.14 6.69 16.22 7.78L13 11H20V4L17.65 6.35Z" fill="currentColor"/>
                          </svg>
                        </ActionButton>
                        <ActionButton title="Экспортировать" onClick={() => handleExportChat(chat.id)}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 9H15V3H9V9H5L12 16L19 9ZM5 18V20H19V18H5Z" fill="currentColor"/>
                          </svg>
                        </ActionButton>
                      </ChatActions>
                    </ChatItem>
                  ))}
                </ChatList>
              ) : (
                <div style={{ textAlign: 'center', padding: '32px', color: colors.paleBlack }}>
                  {searchTerm || activeFilter !== 'all' ? (
                    <p>По вашему запросу ничего не найдено</p>
                  ) : (
                    <p>Архив запросов пуст</p>
                  )}
                </div>
              )}
            </ContentContainer>
          )}
        </Container>
      </MainContent>
      
      <Footer />
    </PageContainer>
  );
};

export default UserProfilePage; 