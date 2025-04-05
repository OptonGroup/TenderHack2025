import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './pages/MainPage.tsx';
import RegisterPage from './pages/RegisterPage.tsx';
import LoginPage from './pages/LoginPage.tsx';
import AdminPanel from './pages/AdminPanel.tsx';
import './styles/global.css';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Router>
  );
};

export default App; 