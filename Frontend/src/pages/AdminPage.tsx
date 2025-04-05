import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../styles/theme.ts';
import Header from '../components/Header.tsx';
import Footer from '../components/Footer.tsx';

// Основные контейнеры для страницы
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

// Заголовок и основные элементы
const AdminHeader = styled.div`
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

const AdminTitle = styled.h1`
  font-size: 28px;
  font-weight: 600;
  color: ${colors.black};
  
  @media (max-width: 768px) {
    font-size: 24px;
  }
`;

const AdminActions = styled.div`
  display: flex;
  gap: 16px;
  
  @media (max-width: 480px) {
    width: 100%;
    flex-direction: column;
  }
`;

// Базовые кнопки
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

// Навигация по вкладкам
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

// Общий контейнер для содержимого
const ContentContainer = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.small};
  padding: 24px;
  
  @media (max-width: 768px) {
    padding: 16px;
  }
`;

// Простая заглушка для админ страницы
const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'users' | 'chats' | 'tickets'>('dashboard');
  const [adminName, setAdminName] = useState('Администратор');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Имитация загрузки данных
    const loadData = async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Загружаем имя администратора из localStorage (имитация)
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        if (userData.role === 'admin') {
          setAdminName(userData.name || 'Администратор');
        } else {
          // Если пользователь не админ, перенаправляем на главную
          window.location.href = '/';
        }
      }
      
      setLoading(false);
    };
    
    loadData();
  }, []);
  
  if (loading) {
    return (
      <PageContainer>
        <Header isLoggedIn={true} userName={adminName} />
        <MainContent>
          <Container>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
              <div>Загрузка...</div>
            </div>
          </Container>
        </MainContent>
        <Footer />
      </PageContainer>
    );
  }
  
  return (
    <PageContainer>
      <Header isLoggedIn={true} userName={adminName} />
      
      <MainContent>
        <Container>
          <AdminHeader>
            <AdminTitle>Панель администратора</AdminTitle>
            <AdminActions>
              <SecondaryButton>Настройки</SecondaryButton>
              <PrimaryButton>Новое объявление</PrimaryButton>
            </AdminActions>
          </AdminHeader>
          
          <TabsContainer>
            <Tab 
              active={activeTab === 'dashboard'} 
              onClick={() => setActiveTab('dashboard')}
            >
              Дашборд
            </Tab>
            <Tab 
              active={activeTab === 'users'} 
              onClick={() => setActiveTab('users')}
            >
              Пользователи
            </Tab>
            <Tab 
              active={activeTab === 'chats'} 
              onClick={() => setActiveTab('chats')}
            >
              Чаты
            </Tab>
            <Tab 
              active={activeTab === 'tickets'} 
              onClick={() => setActiveTab('tickets')}
            >
              Тикеты
            </Tab>
          </TabsContainer>
          
          <ContentContainer>
            {activeTab === 'dashboard' && (
              <div>
                <h2>Дашборд</h2>
                <p>Содержимое дашборда администратора будет отображено здесь.</p>
              </div>
            )}
            
            {activeTab === 'users' && (
              <div>
                <h2>Управление пользователями</h2>
                <p>Список пользователей и функции управления будут отображены здесь.</p>
              </div>
            )}
            
            {activeTab === 'chats' && (
              <div>
                <h2>Мониторинг чатов</h2>
                <p>Список активных чатов и функции управления будут отображены здесь.</p>
              </div>
            )}
            
            {activeTab === 'tickets' && (
              <div>
                <h2>Тикеты и заявки</h2>
                <p>Список тикетов и функции управления будут отображены здесь.</p>
              </div>
            )}
          </ContentContainer>
        </Container>
      </MainContent>
      
      <Footer />
    </PageContainer>
  );
};

export default AdminPage; 