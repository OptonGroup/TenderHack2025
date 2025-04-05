import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows } from '../styles/theme.ts';
import { Navigate } from 'react-router-dom';
import DashboardComponent from '../components/admin/DashboardComponent.tsx';
import UsersManagement from '../components/admin/UsersManagement.tsx';
import ChatsManagement from '../components/admin/ChatsManagement.tsx';

// Стили для админ-панели
const AdminPanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${colors.lightBg};
`;

const AdminHeader = styled.header`
  background-color: ${colors.white};
  border-bottom: 1px solid ${colors.grayBlue};
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: ${shadows.small};
`;

const HeaderTitle = styled.h1`
  font-size: 20px;
  font-weight: 500;
  color: ${colors.black};
  margin: 0;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const UserAvatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: ${colors.mainBlue};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.white};
  font-weight: 500;
`;

const UserName = styled.div`
  font-weight: 500;
`;

const UserRole = styled.div`
  font-size: 12px;
  color: ${colors.paleBlack};
`;

const AdminContent = styled.main`
  flex-grow: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid ${colors.grayBlue};
  margin-bottom: 24px;
  overflow-x: auto;
  
  &::-webkit-scrollbar {
    display: none;
  }
  
  -ms-overflow-style: none;
  scrollbar-width: none;
`;

const TabButton = styled.button<{ active?: boolean }>`
  padding: 12px 24px;
  font-size: 16px;
  font-weight: ${props => props.active ? 500 : 400};
  color: ${props => props.active ? colors.mainBlue : colors.paleBlack};
  background-color: transparent;
  border: none;
  border-bottom: 2px solid ${props => props.active ? colors.mainBlue : 'transparent'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    color: ${colors.mainBlue};
  }
`;

// Компонент админ-панели
const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'users' | 'chats' | 'tickets'>('dashboard');
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(true); // В реальном приложении это будет проверка прав доступа
  
  // Имитация загрузки данных
  useEffect(() => {
    const initAdminPanel = async () => {
      try {
        // Здесь будет проверка прав доступа и загрузка первоначальных данных
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // В реальном приложении здесь будет проверка на роль пользователя
        setIsAdmin(true);
      } catch (error) {
        console.error('Ошибка при инициализации админ-панели:', error);
        setIsAdmin(false);
      } finally {
        setLoading(false);
      }
    };
    
    initAdminPanel();
  }, []);
  
  // Обработчик изменения вкладки
  const handleTabChange = (tab: 'dashboard' | 'users' | 'chats' | 'tickets') => {
    setActiveTab(tab);
  };
  
  // Если у пользователя нет прав администратора, перенаправляем на главную
  if (!loading && !isAdmin) {
    return <Navigate to="/" />;
  }
  
  // Отображаем загрузку, пока проверяем права доступа
  if (loading) {
    return (
      <AdminPanelContainer>
        <AdminHeader>
          <HeaderTitle>Панель администратора</HeaderTitle>
          <div>Загрузка...</div>
        </AdminHeader>
        <AdminContent>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            Загрузка данных...
          </div>
        </AdminContent>
      </AdminPanelContainer>
    );
  }
  
  return (
    <AdminPanelContainer>
      <AdminHeader>
        <HeaderTitle>Панель администратора</HeaderTitle>
        <UserInfo>
          <UserAvatar>А</UserAvatar>
          <div>
            <UserName>Администратор</UserName>
            <UserRole>Администратор системы</UserRole>
          </div>
        </UserInfo>
      </AdminHeader>
      
      <AdminContent>
        <TabsContainer>
          <TabButton 
            active={activeTab === 'dashboard'} 
            onClick={() => handleTabChange('dashboard')}
          >
            Дашборд
          </TabButton>
          <TabButton 
            active={activeTab === 'users'} 
            onClick={() => handleTabChange('users')}
          >
            Пользователи
          </TabButton>
          <TabButton 
            active={activeTab === 'chats'} 
            onClick={() => handleTabChange('chats')}
          >
            Чаты
          </TabButton>
          <TabButton 
            active={activeTab === 'tickets'} 
            onClick={() => handleTabChange('tickets')}
          >
            Обращения
          </TabButton>
        </TabsContainer>
        
        {/* Содержимое вкладки */}
        {activeTab === 'dashboard' && <DashboardComponent />}
        {activeTab === 'users' && <UsersManagement />}
        {activeTab === 'chats' && <ChatsManagement />}
        {activeTab === 'tickets' && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
            <div style={{ textAlign: 'center' }}>
              <h2>Управление обращениями</h2>
              <p>Этот раздел находится в разработке</p>
            </div>
          </div>
        )}
      </AdminContent>
    </AdminPanelContainer>
  );
};

export default AdminPanel; 