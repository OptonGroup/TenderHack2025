import React, { useState } from 'react';
import styled from 'styled-components';
import { colors } from '../styles/theme.ts';
import { Link } from 'react-router-dom';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  padding: 0 24px;
  background-color: ${colors.white};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  
  @media (max-width: 768px) {
    padding: 0 16px;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
`;

const LogoImage = styled.div`
  width: 32px;
  height: 32px;
  background-color: ${colors.red};
  border-radius: 4px;
  margin-right: 12px;
  
  @media (max-width: 480px) {
    width: 28px;
    height: 28px;
    margin-right: 8px;
  }
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;
  
  @media (max-width: 480px) {
    font-size: 14px;
  }
`;

const LogoTitle = styled.span`
  font-weight: 700;
  font-size: 16px;
  color: ${colors.red};
  text-transform: uppercase;
  
  @media (max-width: 480px) {
    font-size: 14px;
  }
`;

const LogoSubtitle = styled.span`
  font-size: 12px;
  color: ${colors.black};
  
  @media (max-width: 480px) {
    font-size: 10px;
  }
`;

const Nav = styled.nav<{ isOpen: boolean }>`
  display: flex;
  align-items: center;
  
  @media (max-width: 768px) {
    position: fixed;
    top: 72px;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: flex-start;
    background-color: ${colors.white};
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 16px;
    transform: translateY(${props => props.isOpen ? '0' : '-100%'});
    opacity: ${props => props.isOpen ? '1' : '0'};
    visibility: ${props => props.isOpen ? 'visible' : 'hidden'};
    transition: all 0.3s ease;
    z-index: 100;
  }
`;

const NavItem = styled.a`
  margin-left: 24px;
  color: ${colors.black};
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s ease;
  
  &:hover {
    color: ${colors.mainBlue};
  }
  
  @media (max-width: 768px) {
    margin-left: 0;
    margin-bottom: 16px;
    font-size: 16px;
    width: 100%;
  }
`;

const SearchBox = styled.div`
  display: flex;
  align-items: center;
  margin-left: 24px;
  
  @media (max-width: 768px) {
    margin-left: 0;
    width: 100%;
  }
`;

const SearchIcon = styled.div`
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.gray};
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
`;

const NotificationIcon = styled.div`
  width: 24px;
  height: 24px;
  margin-right: 16px;
  color: ${colors.black};
  position: relative;
`;

const NotificationBadge = styled.span`
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  background-color: ${colors.red};
  border-radius: 50%;
  color: white;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const UserProfile = styled.div`
  display: flex;
  align-items: center;
  
  @media (max-width: 480px) {
    span {
      display: none;
    }
  }
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: ${colors.grayBlue};
  overflow: hidden;
  margin-right: 8px;
`;

const UserName = styled.span`
  font-size: 14px;
  color: ${colors.black};
  font-weight: 500;
`;

const LoginButton = styled(Link)`
  background-color: ${colors.red};
  color: white;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  text-decoration: none;
  display: inline-block;
  
  &:hover {
    background-color: #c02719;
  }
  
  @media (max-width: 480px) {
    padding: 8px 12px;
    font-size: 12px;
  }
`;

const BurgerMenu = styled.div`
  display: none;
  cursor: pointer;
  
  @media (max-width: 768px) {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 24px;
    height: 18px;
    margin-right: 16px;
  }
`;

const BurgerLine = styled.span<{ isOpen: boolean }>`
  width: 24px;
  height: 2px;
  background-color: ${colors.black};
  transition: all 0.3s ease;
  
  &:first-child {
    transform: ${props => props.isOpen ? 'rotate(45deg) translate(5px, 5px)' : 'rotate(0)'};
  }
  
  &:nth-child(2) {
    opacity: ${props => props.isOpen ? '0' : '1'};
  }
  
  &:last-child {
    transform: ${props => props.isOpen ? 'rotate(-45deg) translate(5px, -5px)' : 'rotate(0)'};
  }
`;

interface HeaderProps {
  isLoggedIn: boolean;
  userName?: string;
  notificationCount?: number;
}

const Header: React.FC<HeaderProps> = ({ isLoggedIn, userName, notificationCount = 0 }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  
  return (
    <HeaderContainer>
      <Logo>
        <LogoImage />
        <LogoText>
          <LogoTitle>ТендерАИ</LogoTitle>
          <LogoSubtitle>Тендерный помощник</LogoSubtitle>
        </LogoText>
      </Logo>
      
      <BurgerMenu onClick={toggleMenu}>
        <BurgerLine isOpen={isMenuOpen} />
        <BurgerLine isOpen={isMenuOpen} />
        <BurgerLine isOpen={isMenuOpen} />
      </BurgerMenu>
      
      <Nav isOpen={isMenuOpen}>
        <NavItem href="#">Главная</NavItem>
        <NavItem href="#">О сервисе</NavItem>
        <NavItem href="#">Тарифы</NavItem>
        <NavItem href="#">Поддержка</NavItem>
      </Nav>
      
      <UserSection>
        {isLoggedIn ? (
          <>
            <NotificationIcon>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
              </svg>
              {notificationCount > 0 && <NotificationBadge>{notificationCount}</NotificationBadge>}
            </NotificationIcon>
            <UserProfile>
              <UserAvatar />
              <UserName>{userName}</UserName>
            </UserProfile>
          </>
        ) : (
          <LoginButton to="/register">Зарегистрироваться</LoginButton>
        )}
      </UserSection>
    </HeaderContainer>
  );
};

export default Header; 