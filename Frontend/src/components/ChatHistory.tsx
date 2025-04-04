import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../styles/theme.ts';

const HistoryContainer = styled.div`
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background-color: ${colors.white};
  box-shadow: ${shadows.large};
  z-index: 1000;
  transform: translateX(100%);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  
  &.open {
    transform: translateX(0);
  }
  
  @media (max-width: 768px) {
    width: 320px;
  }
  
  @media (max-width: 480px) {
    width: 100%;
  }
`;

const HistoryHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: ${colors.paleBlue};
  border-bottom: 1px solid ${colors.grayBlue};
  
  @media (max-width: 480px) {
    padding: 12px 16px;
  }
`;

const HistoryTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: ${colors.black};
  margin: 0;
  
  @media (max-width: 480px) {
    font-size: 16px;
  }
`;

const CloseButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  color: ${colors.black};
  
  &:hover {
    color: ${colors.mainBlue};
  }
`;

const SearchContainer = styled.div`
  padding: 16px 24px;
  border-bottom: 1px solid ${colors.grayBlue};
  
  @media (max-width: 480px) {
    padding: 12px 16px;
  }
`;

const SearchInput = styled.input`
  width: 100%;
  height: 40px;
  padding: 0 16px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.medium};
  font-size: 14px;
  background-color: ${colors.white};
  
  &:focus {
    border-color: ${colors.mainBlue};
    outline: none;
  }
`;

const FilterContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid ${colors.grayBlue};
  overflow-x: auto;
  white-space: nowrap;
  
  &::-webkit-scrollbar {
    height: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${colors.grayBlue};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${colors.mainBlue};
    border-radius: 2px;
  }
  
  @media (max-width: 480px) {
    padding: 10px 16px;
  }
`;

const FilterButton = styled.button<{ active: boolean }>`
  padding: 6px 12px;
  margin-right: 8px;
  background-color: ${props => props.active ? colors.mainBlue : colors.lightBg};
  color: ${props => props.active ? colors.white : colors.black};
  border: 1px solid ${props => props.active ? colors.mainBlue : colors.grayBlue};
  border-radius: ${borderRadius.small};
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.active ? colors.mainBlue : colors.grayBlue};
  }
  
  &:last-child {
    margin-right: 0;
  }
`;

const SortContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  font-size: 12px;
  color: ${colors.paleBlack};
  background-color: ${colors.paleBlue};
  
  @media (max-width: 480px) {
    padding: 10px 16px;
  }
`;

const SortSelect = styled.select`
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  background-color: ${colors.white};
  cursor: pointer;
`;

const HistoryList = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  @media (max-width: 480px) {
    padding: 12px;
    gap: 12px;
  }
`;

const DateDivider = styled.div`
  display: flex;
  align-items: center;
  margin: 8px 0;
  font-size: 12px;
  font-weight: 500;
  color: ${colors.paleBlack};
  
  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background-color: ${colors.grayBlue};
  }
  
  &::before {
    margin-right: 8px;
  }
  
  &::after {
    margin-left: 8px;
  }
`;

const HistoryItem = styled.div`
  padding: 16px;
  background-color: ${colors.lightBg};
  border-radius: ${borderRadius.medium};
  border: 1px solid ${colors.grayBlue};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: ${colors.mainBlue};
    box-shadow: ${shadows.small};
  }
  
  @media (max-width: 480px) {
    padding: 12px;
  }
`;

const HistoryQuestion = styled.div`
  font-weight: 500;
  margin-bottom: 8px;
  
  @media (max-width: 480px) {
    font-size: 14px;
  }
`;

const HistoryAnswer = styled.div`
  font-size: 14px;
  color: ${colors.paleBlack};
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  
  @media (max-width: 480px) {
    font-size: 13px;
  }
`;

const HistoryMeta = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: ${colors.paleBlack};
  
  @media (max-width: 480px) {
    margin-top: 10px;
    font-size: 11px;
  }
`;

const HistoryDate = styled.span``;

const HistoryRating = styled.div`
  display: flex;
  align-items: center;
`;

const RatingIcon = styled.span<{ positive?: boolean }>`
  display: flex;
  align-items: center;
  margin-left: 8px;
  color: ${props => props.positive ? colors.success : colors.error};
`;

const EmptyHistory = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
  color: ${colors.paleBlack};
  height: 100%;
`;

const EmptyIcon = styled.div`
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  color: ${colors.grayBlue};
`;

const EmptyText = styled.div`
  font-size: 14px;
  margin-bottom: 8px;
`;

const EmptySubtext = styled.div`
  font-size: 12px;
`;

const BackToTopButton = styled.button`
  position: sticky;
  bottom: 16px;
  align-self: center;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: ${colors.mainBlue};
  color: ${colors.white};
  border: none;
  box-shadow: ${shadows.medium};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${colors.seaDark};
  }
`;

interface HistoryItemData {
  id: string;
  question: string;
  answer: string;
  date: Date | string;
  rating: 'positive' | 'negative' | null;
}

interface ChatHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectChat: (itemId: string) => void;
  historyItems: HistoryItemData[];
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ 
  isOpen, 
  onClose, 
  onSelectChat, 
  historyItems 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [sortOrder, setSortOrder] = useState('newest');
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [filteredItems, setFilteredItems] = useState<HistoryItemData[]>([]);
  
  // Преобразуем даты в объекты Date, если они строки
  const normalizedItems = historyItems.map(item => ({
    ...item,
    date: typeof item.date === 'string' ? new Date(item.date) : item.date
  }));
  
  useEffect(() => {
    // Применяем фильтрацию и сортировку
    let items = [...normalizedItems];
    
    // Поиск
    if (searchTerm) {
      items = items.filter(item => 
        item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.answer.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Фильтрация по оценке
    if (activeFilter === 'positive') {
      items = items.filter(item => item.rating === 'positive');
    } else if (activeFilter === 'negative') {
      items = items.filter(item => item.rating === 'negative');
    } else if (activeFilter === 'no-rating') {
      items = items.filter(item => item.rating === null);
    }
    
    // Сортировка
    items.sort((a, b) => {
      const dateA = new Date(a.date);
      const dateB = new Date(b.date);
      
      return sortOrder === 'newest' ? dateB.getTime() - dateA.getTime() : dateA.getTime() - dateB.getTime();
    });
    
    setFilteredItems(items);
  }, [normalizedItems, searchTerm, activeFilter, sortOrder]);
  
  // Форматирование даты
  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  // Форматирование даты для группировки
  const formatDateGroup = (date: Date): string => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера';
    } else {
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      }).format(date);
    }
  };
  
  // Группировка истории по датам
  const groupedHistory = filteredItems.reduce<Record<string, HistoryItemData[]>>((acc, item) => {
    const dateGroup = formatDateGroup(new Date(item.date));
    
    if (!acc[dateGroup]) {
      acc[dateGroup] = [];
    }
    
    acc[dateGroup].push(item);
    return acc;
  }, {});
  
  // Обработчик прокрутки для кнопки "наверх"
  const handleScroll = (event: React.UIEvent<HTMLDivElement>) => {
    const target = event.target as HTMLDivElement;
    setShowBackToTop(target.scrollTop > 200);
  };
  
  // Прокрутка к началу списка
  const scrollToTop = () => {
    const historyList = document.querySelector('#history-list');
    if (historyList) {
      historyList.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <HistoryContainer className={isOpen ? 'open' : ''}>
      <HistoryHeader>
        <HistoryTitle>История запросов</HistoryTitle>
        <CloseButton onClick={onClose} aria-label="Закрыть">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        </CloseButton>
      </HistoryHeader>
      
      <SearchContainer>
        <SearchInput 
          type="text" 
          placeholder="Поиск в истории" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          aria-label="Поиск в истории запросов"
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
          active={activeFilter === 'positive'} 
          onClick={() => setActiveFilter('positive')}
        >
          С положительной оценкой
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'negative'} 
          onClick={() => setActiveFilter('negative')}
        >
          С отрицательной оценкой
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'no-rating'} 
          onClick={() => setActiveFilter('no-rating')}
        >
          Без оценки
        </FilterButton>
      </FilterContainer>
      
      <SortContainer>
        <span>Найдено запросов: {filteredItems.length}</span>
        <div>
          <span>Сортировка: </span>
          <SortSelect 
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            aria-label="Сортировка запросов"
          >
            <option value="newest">Сначала новые</option>
            <option value="oldest">Сначала старые</option>
          </SortSelect>
        </div>
      </SortContainer>
      
      <HistoryList id="history-list" onScroll={handleScroll}>
        {filteredItems.length > 0 ? (
          Object.entries(groupedHistory).map(([dateGroup, items]) => (
            <React.Fragment key={dateGroup}>
              <DateDivider>{dateGroup}</DateDivider>
              {items.map(item => (
                <HistoryItem key={item.id} onClick={() => onSelectChat(item.id)}>
                  <HistoryQuestion>{item.question}</HistoryQuestion>
                  <HistoryAnswer>{item.answer}</HistoryAnswer>
                  <HistoryMeta>
                    <HistoryDate>{formatDate(new Date(item.date))}</HistoryDate>
                    <HistoryRating>
                      {item.rating && (
                        <>
                          Оценка:
                          {item.rating === 'positive' ? (
                            <RatingIcon positive>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M1 21H5V9H1V21ZM23 10C23 8.9 22.1 8 21 8H14.69L15.64 3.43L15.67 3.11C15.67 2.7 15.5 2.32 15.23 2.05L14.17 1L7.59 7.59C7.22 7.95 7 8.45 7 9V19C7 20.1 7.9 21 9 21H18C18.83 21 19.54 20.5 19.84 19.78L22.86 12.73C22.95 12.5 23 12.26 23 12V10Z" fill="currentColor"/>
                              </svg>
                            </RatingIcon>
                          ) : (
                            <RatingIcon>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M15 3H6C5.17 3 4.46 3.5 4.16 4.22L1.14 11.27C1.05 11.5 1 11.74 1 12V14C1 15.1 1.9 16 3 16H9.31L8.36 20.57L8.33 20.89C8.33 21.3 8.5 21.68 8.77 21.95L9.83 23L16.41 16.41C16.78 16.05 17 15.55 17 15V5C17 3.9 16.1 3 15 3ZM23 3V15H19V3H23Z" fill="currentColor"/>
                              </svg>
                            </RatingIcon>
                          )}
                        </>
                      )}
                    </HistoryRating>
                  </HistoryMeta>
                </HistoryItem>
              ))}
            </React.Fragment>
          ))
        ) : (
          <EmptyHistory>
            <EmptyIcon>
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 3C8.03 3 4 7.03 4 12H1L4.89 15.89L4.96 16.03L9 12H6C6 8.13 9.13 5 13 5C16.87 5 20 8.13 20 12C20 15.87 16.87 19 13 19C11.07 19 9.32 18.21 8.06 16.94L6.64 18.36C8.27 19.99 10.51 21 13 21C17.97 21 22 16.97 22 12C22 7.03 17.97 3 13 3ZM12 8V13L16.28 15.54L17 14.33L13.5 12.25V8H12Z" fill="currentColor"/>
              </svg>
            </EmptyIcon>
            {searchTerm || activeFilter !== 'all' ? (
              <>
                <EmptyText>По вашему запросу ничего не найдено</EmptyText>
                <EmptySubtext>Попробуйте изменить параметры поиска</EmptySubtext>
              </>
            ) : (
              <>
                <EmptyText>История запросов пуста</EmptyText>
                <EmptySubtext>Начните общение с ассистентом</EmptySubtext>
              </>
            )}
          </EmptyHistory>
        )}
        
        {showBackToTop && (
          <BackToTopButton onClick={scrollToTop} aria-label="Прокрутить наверх">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 8L6 14L7.41 15.41L12 10.83L16.59 15.41L18 14L12 8Z" fill="currentColor"/>
            </svg>
          </BackToTopButton>
        )}
      </HistoryList>
    </HistoryContainer>
  );
};

export default ChatHistory; 