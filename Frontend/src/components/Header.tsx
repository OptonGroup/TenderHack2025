import React from 'react';
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
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;
`;

const LogoTitle = styled.span`
  font-weight: 700;
  font-size: 16px;
  color: ${colors.red};
  text-transform: uppercase;
`;

const LogoSubtitle = styled.span`
  font-size: 12px;
  color: ${colors.black};
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
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
`;

const SearchBox = styled.div`
  display: flex;
  align-items: center;
  margin-left: 24px;
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
`;

interface HeaderProps {
  isLoggedIn: boolean;
  userName?: string;
  notificationCount?: number;
}

const Header: React.FC<HeaderProps> = ({ isLoggedIn, userName, notificationCount = 0 }) => {
  return (
    <HeaderContainer>
      <Logo>
        <LogoImage />
        <LogoText>
          <LogoTitle>Портал</LogoTitle>
          <LogoSubtitle>поставщиков</LogoSubtitle>
        </LogoText>
      </Logo>
      
      <Nav>
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