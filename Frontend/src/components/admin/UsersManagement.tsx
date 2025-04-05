import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../../styles/theme.ts';

// Стили для управления пользователями
const UsersContainer = styled.div`
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

const Table = styled.div`
  width: 100%;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  overflow: hidden;
`;

const TableHeader = styled.div`
  display: grid;
  grid-template-columns: 50px 1fr 1fr 1fr 150px 110px;
  background-color: ${colors.paleBlue};
  font-weight: 500;
  padding: 12px 16px;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const TableHeaderCell = styled.div`
  color: ${colors.black};
  font-size: 14px;
`;

const TableRow = styled.div`
  display: grid;
  grid-template-columns: 50px 1fr 1fr 1fr 150px 110px;
  padding: 12px 16px;
  border-bottom: 1px solid ${colors.grayBlue};
  transition: background-color 0.2s ease;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background-color: ${colors.lightBg};
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 8px;
  }
`;

const TableCell = styled.div`
  font-size: 14px;
  display: flex;
  align-items: center;
  
  @media (max-width: 768px) {
    &::before {
      content: attr(data-label);
      font-weight: 500;
      margin-right: 8px;
    }
  }
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

const Badge = styled.span<{ type: 'active' | 'inactive' | 'blocked' }>`
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: ${borderRadius.small};
  font-size: 12px;
  font-weight: 500;
  
  background-color: ${props => {
    switch (props.type) {
      case 'active': return `${colors.success}20`;
      case 'inactive': return `${colors.paleBlack}20`;
      case 'blocked': return `${colors.error}20`;
      default: return `${colors.paleBlack}20`;
    }
  }};
  
  color: ${props => {
    switch (props.type) {
      case 'active': return colors.success;
      case 'inactive': return colors.paleBlack;
      case 'blocked': return colors.error;
      default: return colors.paleBlack;
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
        case 'inactive': return colors.paleBlack;
        case 'blocked': return colors.error;
        default: return colors.paleBlack;
      }
    }};
  }
`;

const Actions = styled.div`
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
  background-color: transparent;
  color: ${colors.paleBlack};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${colors.paleBlue};
    color: ${colors.black};
  }
`;

const Pagination = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  
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
      <UsersContainer>
        <div style={{ textAlign: 'center', padding: '32px' }}>
          Загрузка пользователей...
        </div>
      </UsersContainer>
    );
  }
  
  return (
    <UsersContainer>
      <ToolBar>
        <SearchContainer>
          <SearchIcon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="currentColor"/>
            </svg>
          </SearchIcon>
          <SearchInput
            type="text"
            placeholder="Поиск пользователей..."
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
            active={statusFilter === 'inactive'}
            onClick={() => handleFilterChange('inactive')}
          >
            Неактивные
          </FilterButton>
          <FilterButton 
            active={statusFilter === 'blocked'}
            onClick={() => handleFilterChange('blocked')}
          >
            Заблокированные
          </FilterButton>
        </FiltersContainer>
      </ToolBar>
      
      <Table>
        <TableHeader>
          <TableHeaderCell>ID</TableHeaderCell>
          <TableHeaderCell>Имя</TableHeaderCell>
          <TableHeaderCell>Email</TableHeaderCell>
          <TableHeaderCell>Организация</TableHeaderCell>
          <TableHeaderCell>Статус</TableHeaderCell>
          <TableHeaderCell>Действия</TableHeaderCell>
        </TableHeader>
        
        {paginatedUsers.length > 0 ? (
          paginatedUsers.map(user => (
            <TableRow key={user.id}>
              <TableCell data-label="ID">{user.id}</TableCell>
              <TableCell data-label="Имя">
                <UserAvatar>{user.name.charAt(0)}</UserAvatar>
                <span style={{ marginLeft: '8px' }}>{user.name}</span>
              </TableCell>
              <TableCell data-label="Email">{user.email}</TableCell>
              <TableCell data-label="Организация">{user.organization}</TableCell>
              <TableCell data-label="Статус">
                <Badge type={getStatusBadgeType(user.status)}>
                  {getStatusText(user.status)}
                </Badge>
              </TableCell>
              <TableCell data-label="Действия">
                <Actions>
                  <ActionButton title="Просмотреть" onClick={() => handleViewUser(user.id)}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" fill="currentColor"/>
                    </svg>
                  </ActionButton>
                  <ActionButton title="Редактировать" onClick={() => handleEditUser(user.id)}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 17.25V21H6.75L17.81 9.94L14.06 6.19L3 17.25ZM20.71 7.04C21.1 6.65 21.1 6.02 20.71 5.63L18.37 3.29C17.98 2.9 17.35 2.9 16.96 3.29L15.13 5.12L18.88 8.87L20.71 7.04Z" fill="currentColor"/>
                    </svg>
                  </ActionButton>
                  <ActionButton 
                    title={user.status === 'blocked' ? 'Разблокировать' : 'Заблокировать'} 
                    onClick={() => handleBlockUser(user.id, user.status)}
                  >
                    {user.status === 'blocked' ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor"/>
                        <path d="M12 9C13.1 9 14 8.1 14 7C14 5.9 13.1 5 12 5C10.9 5 10 5.9 10 7C10 8.1 10.9 9 12 9ZM12 11C10.35 11 8 11.83 8 13.5V16H16V13.5C16 11.83 13.65 11 12 11Z" fill="currentColor"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM4 12C4 7.59 7.59 4 12 4C13.74 4 15.35 4.55 16.7 5.5L5.5 16.7C4.55 15.35 4 13.74 4 12ZM12 20C10.26 20 8.65 19.45 7.3 18.5L18.5 7.3C19.45 8.65 20 10.26 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor"/>
                      </svg>
                    )}
                  </ActionButton>
                </Actions>
              </TableCell>
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell colSpan={6} style={{ justifyContent: 'center', padding: '24px' }}>
              Пользователи не найдены
            </TableCell>
          </TableRow>
        )}
      </Table>
      
      {paginatedUsers.length > 0 && (
        <Pagination>
          <PaginationInfo>
            Показано {(currentPage - 1) * usersPerPage + 1}-{Math.min(currentPage * usersPerPage, filteredUsers.length)} из {filteredUsers.length} пользователей
          </PaginationInfo>
          
          <PaginationControls>
            {renderPaginationButtons()}
          </PaginationControls>
        </Pagination>
      )}
    </UsersContainer>
  );
};

export default UsersManagement; 