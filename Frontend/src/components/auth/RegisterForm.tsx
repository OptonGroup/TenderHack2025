import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, borderRadius } from '../../styles/theme.ts';

// Стили для формы регистрации
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

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid ${colors.grayBlue};
  border-radius: ${borderRadius.small};
  transition: border-color 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  
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

const ErrorMessage = styled.div`
  color: ${colors.error};
  font-size: 14px;
  margin-top: 4px;
`;

const SuccessMessage = styled.div`
  color: ${colors.success};
  font-size: 14px;
  margin-top: 4px;
  padding: 12px;
  background-color: ${colors.success}10;
  border-radius: ${borderRadius.small};
  margin-bottom: 16px;
`;

const PrivacyPolicyContainer = styled.div`
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const Checkbox = styled.input`
  margin-right: 8px;
  margin-top: 2px;
`;

const PrivacyPolicyText = styled.label`
  font-size: 14px;
  color: ${colors.paleBlack};
  
  a {
    color: ${colors.mainBlue};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

interface RegisterFormProps {
  onSuccess: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    companyName: '',
    inn: '',
    email: '',
    password: '',
    confirmPassword: '',
    organizationType: '',
    agreeToTerms: false
  });
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };
  
  const validateForm = () => {
    if (!formData.companyName || !formData.inn || !formData.email || !formData.password || 
        !formData.confirmPassword || !formData.organizationType) {
      setError('Пожалуйста, заполните все поля');
      return false;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      return false;
    }
    
    if (!formData.agreeToTerms) {
      setError('Необходимо согласие с условиями пользования');
      return false;
    }
    
    // Проверка формата ИНН
    if (!/^\d{10}$|^\d{12}$/.test(formData.inn)) {
      setError('ИНН должен содержать 10 или 12 цифр');
      return false;
    }
    
    // Проверка длины пароля
    if (formData.password.length < 8) {
      setError('Пароль должен содержать не менее 8 символов');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      setError('');
      setIsLoading(true);
      
      // Имитация API-запроса
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // В реальном приложении здесь будет запрос к API для регистрации
      console.log('Регистрация с данными:', formData);
      
      // Устанавливаем сообщение об успехе
      setSuccess('Регистрация прошла успешно! Теперь вы можете войти в систему.');
      
      // Через 2 секунды переключаемся на форму входа
      setTimeout(() => {
        onSuccess();
      }, 2000);
      
    } catch (err) {
      setError('Ошибка при регистрации. Пожалуйста, попробуйте позже.');
      console.error('Ошибка регистрации:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      {success && <SuccessMessage>{success}</SuccessMessage>}
      
      <FormGroup>
        <Label htmlFor="companyName">Название организации</Label>
        <Input
          id="companyName"
          name="companyName"
          type="text"
          value={formData.companyName}
          onChange={handleChange}
          placeholder="Введите название организации"
          disabled={isLoading}
          required
        />
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="inn">ИНН</Label>
        <Input
          id="inn"
          name="inn"
          type="text"
          value={formData.inn}
          onChange={handleChange}
          placeholder="Введите ИНН организации"
          disabled={isLoading}
          required
        />
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="organizationType">Тип организации</Label>
        <Select
          id="organizationType"
          name="organizationType"
          value={formData.organizationType}
          onChange={handleChange}
          disabled={isLoading}
          required
        >
          <option value="">Выберите тип организации</option>
          <option value="company">Юридическое лицо</option>
          <option value="ip">Индивидуальный предприниматель</option>
          <option value="individual">Физическое лицо</option>
        </Select>
      </FormGroup>
      
      <FormGroup>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="Введите email"
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
      
      <FormGroup>
        <Label htmlFor="confirmPassword">Подтверждение пароля</Label>
        <Input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          placeholder="Повторите пароль"
          disabled={isLoading}
          required
        />
      </FormGroup>
      
      <PrivacyPolicyContainer>
        <Checkbox
          id="agreeToTerms"
          name="agreeToTerms"
          type="checkbox"
          checked={formData.agreeToTerms}
          onChange={handleCheckboxChange}
          disabled={isLoading}
        />
        <PrivacyPolicyText htmlFor="agreeToTerms">
          Я согласен с <a href="#terms" onClick={(e) => e.preventDefault()}>условиями пользования</a> и <a href="#privacy" onClick={(e) => e.preventDefault()}>политикой конфиденциальности</a>
        </PrivacyPolicyText>
      </PrivacyPolicyContainer>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <SubmitButton type="submit" disabled={isLoading}>
        {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
      </SubmitButton>
    </Form>
  );
};

export default RegisterForm; 