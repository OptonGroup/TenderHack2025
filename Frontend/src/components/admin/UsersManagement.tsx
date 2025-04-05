import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../../styles/theme.ts';

// Стили для управления пользователями
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

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  color: #6c757d;
  font-weight: 500;
`;

const Td = styled.td`
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #3f51b5;
  cursor: pointer;
  margin-right: 8px;
  
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
  organization: string;
  status: 'active' | 'inactive' | 'blocked';
  registrationDate: Date;
}

// Компонент управления пользователями
const UsersManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'blocked'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  
  const usersPerPage = 10;
  
  // Загрузка данных
  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      
      try {
        // Имитация запроса к API
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Генерация моковых данных
        const mockUsers = Array.from({ length: 25 }, (_, index) => ({
          id: `user${index + 1}`,
          name: `Пользователь ${index + 1}`,
          email: `user${index + 1}@example.com`,
          organization: `Организация ${index % 5 + 1}`,
          status: ['active', 'inactive', 'blocked'][Math.floor(Math.random() * 3)] as 'active' | 'inactive' | 'blocked',
          registrationDate: new Date(Date.now() - Math.random() * 10000000000)
        }));
        
        setUsers(mockUsers);
        setTotalPages(Math.ceil(mockUsers.length / usersPerPage));
      } catch (error) {
        console.error('Ошибка при загрузке пользователей:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, []);
  
  // Фильтрация пользователей
  const filteredUsers = users.filter(user => {
    // Фильтр по поиску
    const searchMatch = 
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.organization.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Фильтр по статусу
    const statusMatch = statusFilter === 'all' || user.status === statusFilter;
    
    return searchMatch && statusMatch;
  });
  
  // Пагинация
  const paginatedUsers = filteredUsers.slice(
    (currentPage - 1) * usersPerPage,
    currentPage * usersPerPage
  );
  
  // Обработчики событий
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Сбрасываем страницу при поиске
  };
  
  const handleFilterChange = (status: 'all' | 'active' | 'inactive' | 'blocked') => {
    setStatusFilter(status);
    setCurrentPage(1); // Сбрасываем страницу при смене фильтра
  };
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  
  const handleViewUser = (userId: string) => {
    console.log(`Просмотр пользователя с ID: ${userId}`);
    // Здесь будет логика перехода к просмотру пользователя
  };
  
  const handleEditUser = (userId: string) => {
    console.log(`Редактирование пользователя с ID: ${userId}`);
    // Здесь будет логика редактирования пользователя
  };
  
  const handleBlockUser = (userId: string, currentStatus: string) => {
    console.log(`${currentStatus === 'blocked' ? 'Разблокировка' : 'Блокировка'} пользователя с ID: ${userId}`);
    
    // Имитация изменения статуса пользователя
    setUsers(prevUsers => 
      prevUsers.map(user => 
        user.id === userId 
          ? { 
              ...user, 
              status: user.status === 'blocked' ? 'active' : 'blocked' 
            } 
          : user
      )
    );
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
  
  const getStatusBadgeType = (status: string): 'active' | 'inactive' | 'blocked' => {
    switch (status) {
      case 'active': return 'active';
      case 'inactive': return 'inactive';
      case 'blocked': return 'blocked';
      default: return 'inactive';
    }
  };
  
  const getStatusText = (status: string): string => {
    switch (status) {
      case 'active': return 'Активен';
      case 'inactive': return 'Неактивен';
      case 'blocked': return 'Заблокирован';
      default: return 'Неизвестно';
    }
  };
  
  if (loading) {
    return (
      <Container>
        <div style={{ textAlign: 'center', padding: '32px' }}>
          Загрузка пользователей...
        </div>
      </Container>
    );
  }
  
  return (
    <Container>
      <Card>
        <Header>
          <Title>Управление пользователями</Title>
          <Button>Добавить пользователя</Button>
        </Header>
        
        <Table>
          <thead>
            <tr>
              <Th>ID</Th>
              <Th>Имя</Th>
              <Th>Email</Th>
              <Th>Организация</Th>
              <Th>Статус</Th>
              <Th>Действия</Th>
            </tr>
          </thead>
          <tbody>
            {paginatedUsers.map(user => (
              <tr key={user.id}>
                <Td>{user.id}</Td>
                <Td>{user.name}</Td>
                <Td>{user.email}</Td>
                <Td>{user.organization}</Td>
                <Td>{getStatusText(user.status)}</Td>
                <Td>
                  <ActionButton>Редактировать</ActionButton>
                  <ActionButton>Блокировать</ActionButton>
                </Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </Container>
  );
};

export default UsersManagement; 