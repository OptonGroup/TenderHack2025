import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../../styles/theme.ts';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

// Стили модального окна
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background-color: white;
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.medium};
  width: 90%;
  max-width: 450px;
  position: relative;
  overflow: hidden;
  animation: modalFadeIn 0.3s ease;
  
  @keyframes modalFadeIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid ${colors.grayBlue};
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: ${colors.black};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: ${colors.paleBlack};
  font-size: 24px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${colors.lightBg};
  }
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid ${colors.grayBlue};
`;

const TabButton = styled.button<{ active: boolean }>`
  flex: 1;
  background: none;
  border: none;
  border-bottom: 2px solid ${props => props.active ? colors.mainBlue : 'transparent'};
  color: ${props => props.active ? colors.mainBlue : colors.paleBlack};
  font-weight: ${props => props.active ? '500' : '400'};
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    color: ${colors.mainBlue};
  }
`;

const FormContainer = styled.div`
  padding: 24px;
`;

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'login' | 'register';
}

const AuthModal: React.FC<AuthModalProps> = ({ 
  isOpen, 
  onClose,
  initialTab = 'login'
}) => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>(initialTab);
  
  if (!isOpen) return null;
  
  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>
            {activeTab === 'login' ? 'Вход в систему' : 'Регистрация'}
          </ModalTitle>
          <CloseButton onClick={onClose}>
            ×
          </CloseButton>
        </ModalHeader>
        
        <TabsContainer>
          <TabButton 
            active={activeTab === 'login'} 
            onClick={() => setActiveTab('login')}
          >
            Вход
          </TabButton>
          <TabButton 
            active={activeTab === 'register'} 
            onClick={() => setActiveTab('register')}
          >
            Регистрация
          </TabButton>
        </TabsContainer>
        
        <FormContainer>
          {activeTab === 'login' ? (
            <LoginForm onSuccess={onClose} />
          ) : (
            <RegisterForm onSuccess={() => setActiveTab('login')} />
          )}
        </FormContainer>
      </ModalContent>
    </ModalOverlay>
  );
};

export default AuthModal; 