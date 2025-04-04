import React, { useState } from 'react';
import styled from 'styled-components';
import { colors } from '../styles/theme.ts';

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

const LoginButton = styled.button`
  background-color: ${colors.red};
  color: white;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
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
          <LogoTitle>Портал</LogoTitle>
          <LogoSubtitle>поставщиков</LogoSubtitle>
        </LogoText>
      </Logo>
      
      <BurgerMenu onClick={toggleMenu}>
        <BurgerLine isOpen={isMenuOpen} />
        <BurgerLine isOpen={isMenuOpen} />
        <BurgerLine isOpen={isMenuOpen} />
      </BurgerMenu>
      
      <Nav isOpen={isMenuOpen}>
        <NavItem href="#">Меню</NavItem>
        <NavItem href="#">Каталог продукции</NavItem>
        <NavItem href="#">Закупки</NavItem>
        <NavItem href="#">Московская область</NavItem>
        
        <SearchBox>
          <SearchIcon>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12.5 11H11.71L11.43 10.73C12.41 9.59 13 8.11 13 6.5C13 2.91 10.09 0 6.5 0C2.91 0 0 2.91 0 6.5C0 10.09 2.91 13 6.5 13C8.11 13 9.59 12.41 10.73 11.43L11 11.71V12.5L16 17.49L17.49 16L12.5 11ZM6.5 11C4.01 11 2 8.99 2 6.5C2 4.01 4.01 2 6.5 2C8.99 2 11 4.01 11 6.5C11 8.99 8.99 11 6.5 11Z" fill="currentColor"/>
            </svg>
          </SearchIcon>
        </SearchBox>
      </Nav>
      
      <UserSection>
        {isLoggedIn ? (
          <>
            <NotificationIcon>
              <svg width="18" height="20" viewBox="0 0 18 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 20C10.1 20 11 19.1 11 18H7C7 19.1 7.9 20 9 20ZM18 16V17H0V16L2 14V9C2 5.9 4 3.2 7 2.3V2C7 0.9 7.9 0 9 0C10.1 0 11 0.9 11 2V2.3C14 3.2 16 5.9 16 9V14L18 16ZM14 9C14 6.2 11.8 4 9 4C6.2 4 4 6.2 4 9V15H14V9Z" fill="currentColor"/>
              </svg>
              {notificationCount > 0 && <NotificationBadge>{notificationCount}</NotificationBadge>}
            </NotificationIcon>
            <UserProfile>
              <UserAvatar />
              <UserName>{userName}</UserName>
            </UserProfile>
          </>
        ) : (
          <LoginButton>Зарегистрироваться</LoginButton>
        )}
      </UserSection>
    </HeaderContainer>
  );
};

export default Header; 