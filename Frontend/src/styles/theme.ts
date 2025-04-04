export const colors = {
  // Основные цвета
  mainBlue: '#264B82',
  grayBlue: '#D4DBE6',
  paleBlue: '#E7EFF7',
  red: '#DB2B21',
  black: '#1A1A1A',
  paleBlack: '#8C8C8C',
  
  // Дополнительные цвета
  green: '#009B68',
  seaDark: '#167C85',
  seaClear: '#48B8C2',
  orange: '#F67319',
  gray: '#7F8792',
  lightGray: '#C9D1DF',
  
  // Системные цвета
  white: '#FFFFFF',
  lightBg: '#F5F8FA',
  disabledBg: '#EBEEF2',
  disabledText: '#ABB5C2',
  success: '#34C759',
  warning: '#FFC107',
  error: '#FF3B30'
};

export const typography = {
  fontFamily: '"Roboto", "Arial", sans-serif',
  fontWeights: {
    regular: 400,
    medium: 500,
    bold: 700
  },
  fontSize: {
    xs: '12px',
    sm: '14px',
    md: '16px',
    lg: '18px',
    xl: '20px',
    xxl: '24px',
    xxxl: '32px'
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    loose: 1.8
  }
};

export const shadows = {
  small: '0 2px 4px rgba(0, 0, 0, 0.05)',
  medium: '0 4px 8px rgba(0, 0, 0, 0.1)',
  large: '0 8px 16px rgba(0, 0, 0, 0.15)'
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
  xxxl: '64px'
};

export const borderRadius = {
  small: '4px',
  medium: '8px',
  large: '12px',
  circle: '50%'
};

export const breakpoints = {
  xs: '320px',
  sm: '768px',
  md: '1280px',
  lg: '1600px',
  xl: '1920px'
};

const theme = {
  colors,
  typography,
  shadows,
  spacing,
  borderRadius,
  breakpoints
};

export default theme; 