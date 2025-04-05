import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius } from '../../styles/theme.ts';

// Стили для дашборда
const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Card = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
`;

const CardTitle = styled.h3`
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 16px;
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
`;

const StatCard = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
`;

const StatTitle = styled.div`
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 8px;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
`;

const StatIcon = styled.div<{ bgColor: string }>`
  width: 48px;
  height: 48px;
  border-radius: ${borderRadius.small};
  background-color: ${props => props.bgColor}20;
  color: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
`;

const StatTrend = styled.div<{ trend: 'up' | 'down' | 'neutral' }>`
  display: flex;
  align-items: center;
  font-size: 12px;
  color: ${props => {
    if (props.trend === 'up') return colors.success;
    if (props.trend === 'down') return colors.error;
    return colors.paleBlack;
  }};
`;

const Row = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.small};
  padding: 24px;
`;

const ChartHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ChartTitle = styled.div`
  font-weight: 500;
  font-size: 18px;
`;

const TimePeriod = styled.div`
  display: flex;
  gap: 8px;
`;

const PeriodButton = styled.button<{ active?: boolean }>`
  padding: 6px 12px;
  background-color: ${props => props.active ? colors.paleBlue : 'transparent'};
  color: ${props => props.active ? colors.mainBlue : colors.paleBlack};
  border: 1px solid ${props => props.active ? colors.mainBlue : colors.grayBlue};
  border-radius: ${borderRadius.small};
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${colors.paleBlue}50;
  }
`;

const ChartContent = styled.div`
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.paleBlack};
  font-style: italic;
`;

const RecentActivityCard = styled.div`
  background-color: ${colors.white};
  border-radius: ${borderRadius.medium};
  box-shadow: ${shadows.small};
  padding: 24px;
  display: flex;
  flex-direction: column;
`;

const ActivityHeader = styled.div`
  font-weight: 500;
  font-size: 18px;
  margin-bottom: 16px;
`;

const ActivityList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  flex-grow: 1;
`;

const ActivityItem = styled.div`
  display: flex;
  padding: 12px;
  border-radius: ${borderRadius.small};
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: ${colors.lightBg};
  }
`;

const ActivityIcon = styled.div<{ bgColor: string }>`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: ${props => props.bgColor}20;
  color: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
`;

const ActivityContent = styled.div`
  flex-grow: 1;
`;

const ActivityTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
`;

const ActivityDescription = styled.div`
  font-size: 12px;
  color: ${colors.paleBlack};
`;

const ActivityTime = styled.div`
  font-size: 12px;
  color: ${colors.paleBlack};
  min-width: 70px;
  text-align: right;
`;

// Типы данных
interface Stat {
  id: string;
  title: string;
  value: number;
  trend: 'up' | 'down' | 'neutral';
  trendValue: string;
  icon: React.ReactNode;
  color: string;
}

interface Activity {
  id: string;
  title: string;
  description: string;
  time: string;
  icon: React.ReactNode;
  color: string;
}

// Компонент дашборда
const DashboardComponent: React.FC = () => {
  const [stats, setStats] = useState<Stat[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [chartPeriod, setChartPeriod] = useState<'day' | 'week' | 'month' | 'year'>('week');
  const [loading, setLoading] = useState<boolean>(true);
  
  // Загрузка данных
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      
      try {
        // Имитация запроса к API
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Моковые данные для статистики
        const mockStats: Stat[] = [
          {
            id: 'users',
            title: 'Всего пользователей',
            value: 237,
            trend: 'up',
            trendValue: '12%',
            icon: (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 11C17.66 11 18.99 9.66 18.99 8C18.99 6.34 17.66 5 16 5C14.34 5 13 6.34 13 8C13 9.66 14.34 11 16 11ZM8 11C9.66 11 10.99 9.66 10.99 8C10.99 6.34 9.66 5 8 5C6.34 5 5 6.34 5 8C5 9.66 6.34 11 8 11ZM8 13C5.67 13 1 14.17 1 16.5V19H15V16.5C15 14.17 10.33 13 8 13ZM16 13C15.71 13 15.38 13.02 15.03 13.05C16.19 13.89 17 15.02 17 16.5V19H23V16.5C23 14.17 18.33 13 16 13Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.mainBlue
          },
          {
            id: 'chats',
            title: 'Активных чатов',
            value: 54,
            trend: 'up',
            trendValue: '8%',
            icon: (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H6L4 18V4H20V16Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.success
          },
          {
            id: 'queries',
            title: 'Запросов в день',
            value: 428,
            trend: 'up',
            trendValue: '24%',
            icon: (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 9H2V7H7V9ZM7 12H2V14H7V12ZM20.59 19L17 15.41V17H15V21H17V19.59L21.59 15H17V13H22V15H20.59ZM17 3H19V5H17V3ZM17 7H19V9H17V7ZM17 11H19V13H17V11ZM7 5V3H19V5H7ZM7 16H13V18H7V16Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.accent
          },
          {
            id: 'satisfaction',
            title: 'Удовлетворенность',
            value: 92,
            trend: 'neutral',
            trendValue: '0%',
            icon: (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.99 2C6.47 2 2 6.48 2 12C2 17.52 6.47 22 11.99 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 11.99 2ZM12 20C7.58 20 4 16.42 4 12C4 7.58 7.58 4 12 4C16.42 4 20 7.58 20 12C20 16.42 16.42 20 12 20ZM15.5 11C16.33 11 17 10.33 17 9.5C17 8.67 16.33 8 15.5 8C14.67 8 14 8.67 14 9.5C14 10.33 14.67 11 15.5 11ZM8.5 11C9.33 11 10 10.33 10 9.5C10 8.67 9.33 8 8.5 8C7.67 8 7 8.67 7 9.5C7 10.33 7.67 11 8.5 11ZM12 17.5C14.33 17.5 16.31 16.04 17.11 14H6.89C7.69 16.04 9.67 17.5 12 17.5Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.success
          }
        ];
        
        // Моковые данные для активности
        const mockActivities: Activity[] = [
          {
            id: '1',
            title: 'Новый пользователь',
            description: 'ООО "ТехноСтрой" зарегистрировал аккаунт',
            time: '5 мин назад',
            icon: (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 12C17.21 12 19 10.21 19 8C19 5.79 17.21 4 15 4C12.79 4 11 5.79 11 8C11 10.21 12.79 12 15 12ZM15 6C16.1 6 17 6.9 17 8C17 9.1 16.1 10 15 10C13.9 10 13 9.1 13 8C13 6.9 13.9 6 15 6ZM15 14C12.33 14 7 15.34 7 18V20H23V18C23 15.34 17.67 14 15 14ZM9 18C9.22 17.28 12.31 16 15 16C17.7 16 20.8 17.29 21 18H9ZM6 15V12H9V10H6V7H4V10H1V12H4V15H6Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.mainBlue
          },
          {
            id: '2',
            title: 'Завершенный чат',
            description: 'Пользователь ИП Иванов И.И. завершил чат с оценкой 5/5',
            time: '15 мин назад',
            icon: (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.success
          },
          {
            id: '3',
            title: 'Новый тикет',
            description: 'Создан тикет #4578: "Проблема с загрузкой файлов"',
            time: '32 мин назад',
            icon: (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM6 20V4H13V9H18V20H6ZM8 14H16V16H8V14ZM8 10H16V12H8V10Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.accent
          },
          {
            id: '4',
            title: 'Помеченный чат',
            description: 'Администратор отметил чат #1023 как требующий внимания',
            time: '1 час назад',
            icon: (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.error
          },
          {
            id: '5',
            title: 'Блокировка пользователя',
            description: 'Пользователь ООО "СтройТрейд" был заблокирован',
            time: '3 часа назад',
            icon: (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM4 12C4 7.58 7.58 4 12 4C13.85 4 15.55 4.63 16.9 5.69L5.69 16.9C4.63 15.55 4 13.85 4 12ZM12 20C10.15 20 8.45 19.37 7.1 18.31L18.31 7.1C19.37 8.45 20 10.15 20 12C20 16.42 16.42 20 12 20Z" fill="currentColor"/>
              </svg>
            ),
            color: colors.error
          }
        ];
        
        setStats(mockStats);
        setActivities(mockActivities);
      } catch (error) {
        console.error('Ошибка при загрузке данных дашборда:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  // Выбор периода для графика
  const handlePeriodChange = (period: 'day' | 'week' | 'month' | 'year') => {
    setChartPeriod(period);
  };
  
  if (loading) {
    return (
      <DashboardContainer>
        <div style={{ textAlign: 'center', padding: '32px' }}>
          Загрузка данных...
        </div>
      </DashboardContainer>
    );
  }
  
  return (
    <DashboardContainer>
      <StatGrid>
        {stats.map(stat => (
          <StatCard key={stat.id}>
            <StatIcon bgColor={stat.color}>
              {stat.icon}
            </StatIcon>
            <StatTitle>{stat.title}</StatTitle>
            <StatValue>{stat.value}{stat.id === 'satisfaction' && '%'}</StatValue>
            <StatTrend trend={stat.trend}>
              {stat.trend === 'up' && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '4px' }}>
                  <path d="M7 14L12 9L17 14H7Z" fill="currentColor"/>
                </svg>
              )}
              {stat.trend === 'down' && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '4px' }}>
                  <path d="M7 10L12 15L17 10H7Z" fill="currentColor"/>
                </svg>
              )}
              {stat.trendValue} за неделю
            </StatTrend>
          </StatCard>
        ))}
      </StatGrid>
      
      {/* Графики и активность */}
      <Row>
        {/* График активности */}
        <ChartCard>
          <ChartHeader>
            <ChartTitle>Активность пользователей</ChartTitle>
            <TimePeriod>
              <PeriodButton 
                active={chartPeriod === 'day'} 
                onClick={() => handlePeriodChange('day')}
              >
                День
              </PeriodButton>
              <PeriodButton 
                active={chartPeriod === 'week'} 
                onClick={() => handlePeriodChange('week')}
              >
                Неделя
              </PeriodButton>
              <PeriodButton 
                active={chartPeriod === 'month'} 
                onClick={() => handlePeriodChange('month')}
              >
                Месяц
              </PeriodButton>
              <PeriodButton 
                active={chartPeriod === 'year'} 
                onClick={() => handlePeriodChange('year')}
              >
                Год
              </PeriodButton>
            </TimePeriod>
          </ChartHeader>
          <ChartContent>
            [Здесь будет график активности пользователей за выбранный период]
          </ChartContent>
        </ChartCard>
        
        {/* Недавняя активность */}
        <RecentActivityCard>
          <ActivityHeader>Недавняя активность</ActivityHeader>
          <ActivityList>
            {activities.map(activity => (
              <ActivityItem key={activity.id}>
                <ActivityIcon bgColor={activity.color}>
                  {activity.icon}
                </ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>{activity.title}</ActivityTitle>
                  <ActivityDescription>{activity.description}</ActivityDescription>
                </ActivityContent>
                <ActivityTime>{activity.time}</ActivityTime>
              </ActivityItem>
            ))}
          </ActivityList>
        </RecentActivityCard>
      </Row>
    </DashboardContainer>
  );
};

export default DashboardComponent; 