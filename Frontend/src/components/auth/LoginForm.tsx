import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, borderRadius } from '../../styles/theme.ts';

// Стили для формы входа
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

const SubmitButton = styled.button`
  background-color: ${colors.mainBlue};
  color: white;
  border: none;
  border-radius: ${borderRadius.small};
  padding: 12px;
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

const ForgotPassword = styled.button`
  background: none;
  border: none;
  color: ${colors.mainBlue};
  font-size: 14px;
  text-align: right;
  cursor: pointer;
  margin-top: 8px;
  padding: 0;
  align-self: flex-end;
  
  &:hover {
    text-decoration: underline;
  }
`;

const ErrorMessage = styled.div`
  color: ${colors.error};
  font-size: 14px;
  margin-top: 4px;
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 16px;
`;

const Checkbox = styled.input`
  margin-right: 8px;
`;

const CheckboxLabel = styled.label`
  font-size: 14px;
  color: ${colors.paleBlack};
`;

interface LoginFormProps {
  onSuccess: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Пожалуйста, заполните все поля');
      return;
    }
    
    try {
      setError('');
      setIsLoading(true);
      
      // Имитация API-запроса
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // В реальном приложении здесь будет запрос к API для авторизации
      console.log('Вход с данными:', { email, password, rememberMe });
      
      // После успешного входа вызываем onSuccess
      onSuccess();
    } catch (err) {
      setError('Ошибка при входе. Пожалуйста, проверьте введенные данные.');
      console.error('Ошибка входа:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleForgotPassword = () => {
    // Здесь будет логика для восстановления пароля
    console.log('Восстановление пароля');
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      <FormGroup>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Введите ваш email"
          required
        />
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="password">Пароль</Label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Введите пароль"
          required
        />
      </FormGroup>
      
      <CheckboxContainer>
        <Checkbox
          id="rememberMe"
          type="checkbox"
          checked={rememberMe}
          onChange={e => setRememberMe(e.target.checked)}
        />
        <CheckboxLabel htmlFor="rememberMe">Запомнить меня</CheckboxLabel>
      </CheckboxContainer>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <SubmitButton type="submit" disabled={isLoading}>
        {isLoading ? 'Вход...' : 'Войти'}
      </SubmitButton>
      
      <ForgotPassword type="button" onClick={handleForgotPassword}>
        Забыли пароль?
      </ForgotPassword>
    </Form>
  );
};

export default LoginForm; 