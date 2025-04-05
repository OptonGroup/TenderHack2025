import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../styles/theme.ts';
import { Link, useNavigate } from 'react-router-dom';

// Стили для страницы входа
const PageContainer = styled.div`
  min-height: calc(100vh - 72px);
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: ${colors.lightBg};
  padding: 40px 20px;
`;

const FormCard = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.medium};
  width: 100%;
  max-width: 450px;
  overflow: hidden;
`;

const FormHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid ${colors.grayBlue};
`;

const Title = styled.h1`
  font-size: 24px;
  margin: 0;
  color: ${colors.black};
`;

const FormBody = styled.div`
  padding: 24px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: ${colors.black};
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  transition: border-color 0.2s;
  
  &:focus {
    border-color: ${colors.mainBlue};
    outline: none;
  }
`;

const ForgotPassword = styled.div`
  margin-top: -12px;
  margin-bottom: 20px;
  text-align: right;
  
  a {
    font-size: 14px;
    color: ${colors.mainBlue};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const SubmitButton = styled.button`
  background-color: ${colors.mainBlue};
  color: white;
  border: none;
  border-radius: ${borderRadius.small};
  padding: 14px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 8px;
  
  &:hover {
    background-color: ${colors.seaDark};
  }
  
  &:disabled {
    background-color: ${colors.grayBlue};
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: ${colors.error};
  font-size: 14px;
  margin-top: 4px;
  padding: 8px 12px;
  background-color: ${colors.error}10;
  border-radius: ${borderRadius.small};
  margin-bottom: 16px;
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 20px;
`;

const Checkbox = styled.input`
  margin-right: 8px;
`;

const CheckboxLabel = styled.label`
  font-size: 14px;
  color: ${colors.paleBlack};
`;

const RegisterLink = styled.div`
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: ${colors.paleBlack};
  
  a {
    color: ${colors.mainBlue};
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      setError('Пожалуйста, заполните все поля');
      return;
    }
    
    try {
      setError('');
      setIsLoading(true);
      
      // Имитация API-запроса
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // В реальном приложении здесь будет запрос к API для входа
      console.log('Вход с данными:', formData);
      
      // После успешного входа перенаправляем на главную страницу
      navigate('/');
      
    } catch (err) {
      setError('Неверный email или пароль. Пожалуйста, попробуйте еще раз.');
      console.error('Ошибка входа:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleForgotPassword = (e: React.MouseEvent) => {
    e.preventDefault();
    // Здесь будет логика для восстановления пароля
    console.log('Переход на восстановление пароля');
  };
  
  return (
    <PageContainer>
      <FormCard>
        <FormHeader>
          <Title>Вход в систему</Title>
        </FormHeader>
        
        <FormBody>
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Введите ваш email"
                disabled={isLoading}
                required
              />
            </FormGroup>
            
            <FormGroup>
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Введите пароль"
                disabled={isLoading}
                required
              />
            </FormGroup>
            
            <ForgotPassword>
              <a href="#" onClick={handleForgotPassword}>Забыли пароль?</a>
            </ForgotPassword>
            
            <CheckboxContainer>
              <Checkbox
                id="rememberMe"
                name="rememberMe"
                type="checkbox"
                checked={formData.rememberMe}
                onChange={handleChange}
                disabled={isLoading}
              />
              <CheckboxLabel htmlFor="rememberMe">Запомнить меня</CheckboxLabel>
            </CheckboxContainer>
            
            {error && <ErrorMessage>{error}</ErrorMessage>}
            
            <SubmitButton type="submit" disabled={isLoading}>
              {isLoading ? 'Вход...' : 'Войти'}
            </SubmitButton>
          </Form>
          
          <RegisterLink>
            Еще нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
          </RegisterLink>
        </FormBody>
      </FormCard>
    </PageContainer>
  );
};

export default LoginPage; 