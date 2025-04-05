import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../styles/theme.ts';
import Header from '../components/Header.tsx';
import Footer from '../components/Footer.tsx';

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${colors.lightBg};
`;

const MainContent = styled.main`
  flex: 1;
  padding: 48px 0;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const AuthContainer = styled.div`
  width: 100%;
  max-width: 480px;
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.medium};
  overflow: hidden;
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid ${colors.grayBlue};
`;

const Tab = styled.button<{ active: boolean }>`
  flex: 1;
  padding: 16px;
  font-size: 16px;
  font-weight: 500;
  background-color: ${props => props.active ? colors.white : colors.paleBlue};
  color: ${props => props.active ? colors.black : colors.paleBlack};
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.active ? colors.white : colors.grayBlue};
  }
`;

const FormContainer = styled.div`
  padding: 32px;
  
  @media (max-width: 480px) {
    padding: 24px 16px;
  }
`;

const FormTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  text-align: center;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: ${colors.black};
`;

const Input = styled.input`
  width: 100%;
  height: 48px;
  padding: 0 16px;
  font-size: 14px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  
  &:focus {
    border-color: ${colors.mainBlue};
    outline: none;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  height: 48px;
  background-color: ${colors.red};
  color: white;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: ${borderRadius.small};
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #c02719;
  }
  
  &:disabled {
    background-color: ${colors.grayBlue};
    cursor: not-allowed;
  }
`;

const ForgotPassword = styled.a`
  display: block;
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: ${colors.mainBlue};
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
`;

const ErrorMessage = styled.div`
  color: ${colors.error};
  font-size: 14px;
  margin-top: 4px;
`;

const SuccessMessage = styled.div`
  color: ${colors.success};
  font-size: 14px;
  text-align: center;
  margin-bottom: 16px;
  padding: 8px;
  background-color: #e6f7e6;
  border-radius: ${borderRadius.small};
`;

const AuthPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    organization: '',
  });
  const [errors, setErrors] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    general: '',
  });
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Сбрасываем ошибку при изменении поля
    if (name in errors) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors = {
      email: '',
      password: '',
      confirmPassword: '',
      general: '',
    };
    
    // Валидация email
    if (!formData.email) {
      newErrors.email = 'Введите email';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Некорректный email';
    }
    
    // Валидация пароля
    if (!formData.password) {
      newErrors.password = 'Введите пароль';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Пароль должен содержать минимум 6 символов';
    }
    
    // Дополнительная валидация для регистрации
    if (activeTab === 'register') {
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Пароли не совпадают';
      }
    }
    
    setErrors(newErrors);
    
    // Проверяем, есть ли ошибки
    return !Object.values(newErrors).some(error => error);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    setSuccess('');
    
    try {
      // Имитация запроса к API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // В реальном приложении здесь будет запрос к API для авторизации
      // const response = await fetch('/api/login', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email: formData.email, password: formData.password }),
      // });
      
      // if (!response.ok) {
      //   throw new Error('Неверный email или пароль');
      // }
      
      // const data = await response.json();
      // localStorage.setItem('token', data.token);
      // localStorage.setItem('user', JSON.stringify(data.user));
      
      // Простая имитация для демонстрации
      localStorage.setItem('token', 'demo-token');
      localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Александр Семенов',
        email: formData.email,
        role: formData.email.includes('admin') ? 'admin' : 'user',
      }));
      
      // Перенаправление на главную страницу
      window.location.href = '/';
    } catch (error) {
      setErrors(prev => ({ ...prev, general: 'Ошибка авторизации. Пожалуйста, проверьте email и пароль.' }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    setSuccess('');
    
    try {
      // Имитация запроса к API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // В реальном приложении здесь будет запрос к API для регистрации
      // const response = await fetch('/api/register', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     email: formData.email,
      //     password: formData.password,
      //     name: formData.name,
      //     organization: formData.organization,
      //   }),
      // });
      
      // if (!response.ok) {
      //   throw new Error('Ошибка регистрации');
      // }
      
      setSuccess('Регистрация успешно завершена! Теперь вы можете войти в систему.');
      setActiveTab('login');
      setFormData(prev => ({
        ...prev,
        password: '',
        confirmPassword: '',
      }));
    } catch (error) {
      setErrors(prev => ({ ...prev, general: 'Ошибка регистрации. Пожалуйста, попробуйте позже.' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageContainer>
      <Header 
        isLoggedIn={false}
      />
      
      <MainContent>
        <AuthContainer>
          <TabContainer>
            <Tab 
              active={activeTab === 'login'} 
              onClick={() => setActiveTab('login')}
            >
              Вход
            </Tab>
            <Tab 
              active={activeTab === 'register'} 
              onClick={() => setActiveTab('register')}
            >
              Регистрация
            </Tab>
          </TabContainer>
          
          <FormContainer>
            {success && <SuccessMessage>{success}</SuccessMessage>}
            
            {activeTab === 'login' ? (
              <>
                <FormTitle>Вход в личный кабинет</FormTitle>
                <form onSubmit={handleLogin}>
                  <FormGroup>
                    <Label htmlFor="email">Email</Label>
                    <Input 
                      type="email" 
                      id="email" 
                      name="email" 
                      value={formData.email} 
                      onChange={handleInputChange} 
                      placeholder="example@mail.ru"
                      required
                    />
                    {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
                  </FormGroup>
                  
                  <FormGroup>
                    <Label htmlFor="password">Пароль</Label>
                    <Input 
                      type="password" 
                      id="password" 
                      name="password" 
                      value={formData.password} 
                      onChange={handleInputChange} 
                      placeholder="Введите пароль"
                      required
                    />
                    {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
                  </FormGroup>
                  
                  {errors.general && <ErrorMessage>{errors.general}</ErrorMessage>}
                  
                  <SubmitButton type="submit" disabled={isLoading}>
                    {isLoading ? 'Вход...' : 'Войти'}
                  </SubmitButton>
                  
                  <ForgotPassword href="#">Забыли пароль?</ForgotPassword>
                </form>
              </>
            ) : (
              <>
                <FormTitle>Регистрация</FormTitle>
                <form onSubmit={handleRegister}>
                  <FormGroup>
                    <Label htmlFor="email">Email</Label>
                    <Input 
                      type="email" 
                      id="email" 
                      name="email" 
                      value={formData.email} 
                      onChange={handleInputChange} 
                      placeholder="example@mail.ru"
                      required
                    />
                    {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
                  </FormGroup>
                  
                  <FormGroup>
                    <Label htmlFor="name">ФИО</Label>
                    <Input 
                      type="text" 
                      id="name" 
                      name="name" 
                      value={formData.name} 
                      onChange={handleInputChange} 
                      placeholder="Иванов Иван Иванович"
                      required
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <Label htmlFor="organization">Организация</Label>
                    <Input 
                      type="text" 
                      id="organization" 
                      name="organization" 
                      value={formData.organization} 
                      onChange={handleInputChange} 
                      placeholder="ООО 'Компания'"
                      required
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <Label htmlFor="password">Пароль</Label>
                    <Input 
                      type="password" 
                      id="password" 
                      name="password" 
                      value={formData.password} 
                      onChange={handleInputChange} 
                      placeholder="Минимум 6 символов"
                      required
                    />
                    {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
                  </FormGroup>
                  
                  <FormGroup>
                    <Label htmlFor="confirmPassword">Подтверждение пароля</Label>
                    <Input 
                      type="password" 
                      id="confirmPassword" 
                      name="confirmPassword" 
                      value={formData.confirmPassword} 
                      onChange={handleInputChange} 
                      placeholder="Повторите пароль"
                      required
                    />
                    {errors.confirmPassword && <ErrorMessage>{errors.confirmPassword}</ErrorMessage>}
                  </FormGroup>
                  
                  {errors.general && <ErrorMessage>{errors.general}</ErrorMessage>}
                  
                  <SubmitButton type="submit" disabled={isLoading}>
                    {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                  </SubmitButton>
                </form>
              </>
            )}
          </FormContainer>
        </AuthContainer>
      </MainContent>
      
      <Footer />
    </PageContainer>
  );
};

export default AuthPage; 