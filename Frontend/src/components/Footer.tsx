import React from 'react';
import styled from 'styled-components';
import { colors } from '../styles/theme.ts';

const FooterContainer = styled.footer`
  background-color: ${colors.paleBlue};
  padding: 32px 24px;
  
  @media (max-width: 480px) {
    padding: 24px 16px;
  }
`;

const FooterContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const FooterLinks = styled.div`
  display: flex;
  
  @media (max-width: 768px) {
    margin-bottom: 24px;
    width: 100%;
  }
  
  @media (max-width: 480px) {
    flex-direction: column;
  }
`;

const LinkGroup = styled.div`
  margin-right: 48px;
  
  &:last-child {
    margin-right: 0;
  }
  
  @media (max-width: 768px) {
    margin-right: 24px;
  }
  
  @media (max-width: 480px) {
    margin-right: 0;
    margin-bottom: 20px;
  }
`;

const FooterLink = styled.a`
  display: block;
  color: ${colors.black};
  font-size: 14px;
  margin-bottom: 12px;
  transition: color 0.2s ease;
  
  &:hover {
    color: ${colors.mainBlue};
  }
  
  @media (max-width: 480px) {
    margin-bottom: 10px;
  }
`;

const SupportSection = styled.div`
  display: flex;
  flex-direction: column;
  
  @media (max-width: 768px) {
    width: 100%;
  }
`;

const SupportTitle = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: ${colors.black};
  
  @media (max-width: 480px) {
    margin-bottom: 10px;
  }
`;

const SupportIcon = styled.div`
  margin-right: 8px;
  color: ${colors.mainBlue};
`;

const SocialLinks = styled.div`
  display: flex;
  margin-top: 16px;
`;

const SocialLink = styled.a`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: ${colors.mainBlue};
  margin-right: 12px;
  color: white;
  
  &:last-child {
    margin-right: 0;
  }
  
  &:hover {
    background-color: ${colors.seaDark};
  }
`;

const Copyright = styled.div`
  font-size: 12px;
  color: ${colors.paleBlack};
  margin-top: 32px;
  text-align: center;
  
  @media (max-width: 480px) {
    margin-top: 24px;
    font-size: 11px;
  }
`;

const Footer: React.FC = () => {
  return (
    <FooterContainer>
      <FooterContent>
        <FooterLinks>
          <LinkGroup>
            <FooterLink href="#">О портале</FooterLink>
            <FooterLink href="#">Поставщикам</FooterLink>
            <FooterLink href="#">Новости</FooterLink>
            <FooterLink href="#">Контакты</FooterLink>
            <FooterLink href="#">Карта сайта</FooterLink>
          </LinkGroup>
        </FooterLinks>
        
        <SupportSection>
          <SupportTitle>
            <SupportIcon>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 0C4.03 0 0 4.03 0 9C0 13.97 4.03 18 9 18C13.97 18 18 13.97 18 9C18 4.03 13.97 0 9 0ZM9 16.2C5.04 16.2 1.8 12.96 1.8 9C1.8 5.04 5.04 1.8 9 1.8C12.96 1.8 16.2 5.04 16.2 9C16.2 12.96 12.96 16.2 9 16.2Z" fill="currentColor"/>
                <path d="M9 12.6C9.5 12.6 9.9 12.2 9.9 11.7C9.9 11.2 9.5 10.8 9 10.8C8.5 10.8 8.1 11.2 8.1 11.7C8.1 12.2 8.5 12.6 9 12.6Z" fill="currentColor"/>
                <path d="M9 4.5C7.9 4.5 6.93 5.13 6.48 6.09C6.3 6.48 6.5 6.9 6.8 7.08C7.2 7.26 7.62 7.05 7.8 6.75C8 6.3 8.48 6 9 6C9.75 6 10.5 6.45 10.5 7.2C10.5 7.95 9.8 8.28 9.35 8.67C8.9 9.06 8.55 9.6 8.55 10.2H8.55C8.55 10.6 8.85 10.95 9.25 10.95C9.65 10.95 9.95 10.65 9.95 10.25C9.95 10 10.07 9.78 10.45 9.45C10.83 9.12 11.55 8.55 11.55 7.3C11.55 5.8 10.4 4.5 9 4.5Z" fill="currentColor"/>
              </svg>
            </SupportIcon>
            Служба качества
          </SupportTitle>
          
          <SupportTitle>
            <SupportIcon>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 0C4.03 0 0 4.03 0 9C0 13.97 4.03 18 9 18C13.97 18 18 13.97 18 9C18 4.03 13.97 0 9 0ZM9 16.2C5.04 16.2 1.8 12.96 1.8 9C1.8 5.04 5.04 1.8 9 1.8C12.96 1.8 16.2 5.04 16.2 9C16.2 12.96 12.96 16.2 9 16.2Z" fill="currentColor"/>
                <path d="M8.1 4.5H9.9V9.9H8.1V4.5ZM8.1 11.7H9.9V13.5H8.1V11.7Z" fill="currentColor"/>
              </svg>
            </SupportIcon>
            Написать в службу поддержки
          </SupportTitle>
          
          <SocialLinks>
            <SocialLink href="#">
              <svg width="10" height="18" viewBox="0 0 10 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.5 3H7.5C6.95 3 6.5 3.45 6.5 4V6H9.5C9.6 6 9.7 6.05 9.75 6.15C9.8 6.25 9.8 6.35 9.75 6.45L9.1 8.45C9 8.75 8.75 8.95 8.45 8.95H6.5V17.5C6.5 17.75 6.25 18 6 18H4C3.75 18 3.5 17.75 3.5 17.5V8.95H1.5C1.25 8.95 1 8.7 1 8.45V6.45C1 6.2 1.25 5.95 1.5 5.95H3.5V4C3.5 1.8 5.3 0 7.5 0H9.5C9.75 0 10 0.25 10 0.5V2.5C10 2.75 9.75 3 9.5 3Z" fill="white"/>
              </svg>
            </SocialLink>
            <SocialLink href="#">
              <svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.69 1.89C19.69 1.86 19.7 1.84 19.7 1.81C19.9 1.31 20 0.58 19.53 0C19.53 0 19.53 0 19.52 0C19.1 0 18.58 0.16 17.9 0.85C17.9 0.85 17.9 0.85 17.9 0.85C16.3 0.28 14.55 0 12.8 0H7.2C5.45 0 3.7 0.28 2.1 0.85C2.1 0.85 2.1 0.85 2.1 0.85C1.42 0.16 0.9 0 0.48 0C0.47 0 0.47 0 0.47 0C0 0.58 0.1 1.31 0.3 1.81C0.3 1.84 0.31 1.86 0.31 1.89C0.08 2.55 0 3.27 0 4C0 5.47 0.3 6.95 1.2 8.05C2.25 9.33 3.85 10 5.7 10C5.88 10 6.06 9.97 6.25 9.95C6.58 9.89 6.92 9.8 7.23 9.68C7.46 10.41 7.9 11.06 8.5 11.54C9.15 12.04 9.95 12.3 10.8 12.3H11.55V15.25C11.55 15.66 11.89 16 12.3 16C12.71 16 13.05 15.66 13.05 15.25V12.3H14.7C15.55 12.3 16.35 12.04 17 11.54C17.6 11.06 18.04 10.41 18.27 9.68C18.58 9.8 18.92 9.89 19.25 9.95C19.44 9.97 19.62 10 19.8 10C21.65 10 23.25 9.33 24.3 8.05C25.2 6.95 25.5 5.47 25.5 4C25 3.27 24.92 2.55 24.69 1.89ZM4.2 7.5C3.33 7.5 2.5 7.05 2.5 6C2.5 4.95 3.33 4.5 4.2 4.5C5.07 4.5 5.9 4.95 5.9 6C5.9 7.05 5.08 7.5 4.2 7.5ZM20.8 7.5C19.93 7.5 19.1 7.05 19.1 6C19.1 4.95 19.93 4.5 20.8 4.5C21.67 4.5 22.5 4.95 22.5 6C22.5 7.05 21.68 7.5 20.8 7.5Z" fill="white"/>
              </svg>
            </SocialLink>
            <SocialLink href="#">
              <svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.73 2.46C19.73 2.46 19.57 1.28 19.06 0.77C18.42 0.09 17.7 0.09 17.38 0.05C14.67 -0.15 10.25 -0.15 10.25 -0.15H10.24C10.24 -0.15 5.82 -0.15 3.11 0.05C2.79 0.09 2.07 0.09 1.43 0.77C0.92 1.28 0.76 2.46 0.76 2.46C0.76 2.46 0.58 3.85 0.58 5.23V6.51C0.58 7.89 0.75 9.28 0.75 9.28C0.75 9.28 0.91 10.46 1.42 10.97C2.06 11.65 2.92 11.63 3.28 11.7C4.66 11.84 10.25 11.89 10.25 11.89C10.25 11.89 14.67 11.88 17.38 11.69C17.7 11.65 18.42 11.65 19.06 10.97C19.57 10.46 19.73 9.28 19.73 9.28C19.73 9.28 19.91 7.9 19.91 6.51V5.23C19.91 3.85 19.73 2.46 19.73 2.46ZM8.22 8.07L8.22 3.12L13.43 5.61L8.22 8.07Z" fill="white"/>
              </svg>
            </SocialLink>
            <SocialLink href="#">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 0C7.283 0 6.944 0.0115 5.877 0.06C4.813 0.109 4.086 0.278 3.45 0.525C2.792 0.78 2.234 1.122 1.678 1.678C1.122 2.234 0.78 2.792 0.525 3.45C0.278 4.086 0.109 4.813 0.06 5.877C0.0115 6.944 0 7.283 0 10C0 12.717 0.0115 13.056 0.06 14.123C0.109 15.187 0.278 15.914 0.525 16.55C0.78 17.208 1.122 17.766 1.678 18.322C2.234 18.878 2.792 19.22 3.45 19.475C4.086 19.722 4.813 19.891 5.877 19.94C6.944 19.988 7.283 20 10 20C12.717 20 13.056 19.988 14.123 19.94C15.187 19.891 15.914 19.722 16.55 19.475C17.208 19.22 17.766 18.878 18.322 18.322C18.878 17.766 19.22 17.208 19.475 16.55C19.722 15.914 19.891 15.187 19.94 14.123C19.988 13.056 20 12.717 20 10C20 7.283 19.988 6.944 19.94 5.877C19.891 4.813 19.722 4.086 19.475 3.45C19.22 2.792 18.878 2.234 18.322 1.678C17.766 1.122 17.208 0.78 16.55 0.525C15.914 0.278 15.187 0.109 14.123 0.06C13.056 0.0115 12.717 0 10 0ZM10 1.8C12.67 1.8 12.987 1.812 14.042 1.86C15.021 1.905 15.548 2.067 15.897 2.204C16.366 2.387 16.698 2.603 17.048 2.952C17.397 3.302 17.613 3.634 17.796 4.103C17.933 4.452 18.095 4.979 18.14 5.958C18.188 7.013 18.2 7.33 18.2 10C18.2 12.67 18.188 12.987 18.14 14.042C18.095 15.021 17.933 15.548 17.796 15.897C17.613 16.366 17.397 16.698 17.048 17.048C16.698 17.397 16.366 17.613 15.897 17.796C15.548 17.933 15.021 18.095 14.042 18.14C12.987 18.188 12.671 18.2 10 18.2C7.329 18.2 7.013 18.188 5.958 18.14C4.979 18.095 4.452 17.933 4.103 17.796C3.634 17.613 3.302 17.397 2.952 17.048C2.603 16.698 2.387 16.366 2.204 15.897C2.067 15.548 1.905 15.021 1.86 14.042C1.812 12.987 1.8 12.67 1.8 10C1.8 7.33 1.812 7.013 1.86 5.958C1.905 4.979 2.067 4.452 2.204 4.103C2.387 3.634 2.603 3.302 2.952 2.952C3.302 2.603 3.634 2.387 4.103 2.204C4.452 2.067 4.979 1.905 5.958 1.86C7.013 1.812 7.33 1.8 10 1.8Z" fill="white"/>
                <path d="M10 13.333C8.16 13.333 6.667 11.841 6.667 10C6.667 8.159 8.16 6.667 10 6.667C11.841 6.667 13.333 8.159 13.333 10C13.333 11.841 11.841 13.333 10 13.333ZM10 4.865C7.165 4.865 4.865 7.165 4.865 10C4.865 12.835 7.165 15.135 10 15.135C12.835 15.135 15.135 12.835 15.135 10C15.135 7.165 12.835 4.865 10 4.865Z" fill="white"/>
                <path d="M16.538 4.662C16.538 5.325 16.001 5.862 15.338 5.862C14.675 5.862 14.138 5.325 14.138 4.662C14.138 3.999 14.675 3.462 15.338 3.462C16.001 3.462 16.538 3.999 16.538 4.662Z" fill="white"/>
              </svg>
            </SocialLink>
          </SocialLinks>
        </SupportSection>
      </FooterContent>
      
      <Copyright>
        © 2017-2023 г. Портал поставщиков работает в соответствии с 44-ФЗ
      </Copyright>
    </FooterContainer>
  );
};

export default Footer; 