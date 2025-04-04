import React from 'react';
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
  
  &.open {
    transform: translateX(0);
  }
`;

const HistoryHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: ${colors.paleBlue};
  border-bottom: 1px solid ${colors.grayBlue};
`;

const HistoryTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: ${colors.black};
  margin: 0;
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

const HistoryList = styled.div`
  padding: 16px;
  height: calc(100vh - 65px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
`;

const HistoryQuestion = styled.div`
  font-weight: 500;
  margin-bottom: 8px;
`;

const HistoryAnswer = styled.div`
  font-size: 14px;
  color: ${colors.paleBlack};
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const HistoryMeta = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: ${colors.paleBlack};
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

interface HistoryItemData {
  id: string;
  question: string;
  answer: string;
  date: Date;
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
  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <HistoryContainer className={isOpen ? 'open' : ''}>
      <HistoryHeader>
        <HistoryTitle>История запросов</HistoryTitle>
        <CloseButton onClick={onClose}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        </CloseButton>
      </HistoryHeader>
      
      <HistoryList>
        {historyItems.length > 0 ? (
          historyItems.map(item => (
            <HistoryItem key={item.id} onClick={() => onSelectChat(item.id)}>
              <HistoryQuestion>{item.question}</HistoryQuestion>
              <HistoryAnswer>{item.answer}</HistoryAnswer>
              <HistoryMeta>
                <HistoryDate>{formatDate(item.date)}</HistoryDate>
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
          ))
        ) : (
          <div style={{ textAlign: 'center', color: colors.paleBlack, marginTop: '32px' }}>
            История запросов пуста
          </div>
        )}
      </HistoryList>
    </HistoryContainer>
  );
};

export default ChatHistory; 