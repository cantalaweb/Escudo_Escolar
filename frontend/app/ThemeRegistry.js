'use client';

import { useState, useEffect, useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v16-appRouter';
import { themeOptions } from '../theme';

export default function ThemeRegistry({ children }) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Detectar el modo claro/oscuro del sistema operativo
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      setIsDarkMode(mediaQuery.matches);

      const handleChange = (e) => {
        setIsDarkMode(e.matches);
      };

      mediaQuery.addEventListener('change', handleChange);

      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    }
  }, []);

  // Crear tema dinámico basado en el modo del sistema
  const theme = useMemo(
    () =>
      createTheme({
        ...themeOptions,
        palette: {
          mode: isDarkMode ? 'dark' : 'light',
          ...themeOptions.palette,
        },
      }),
    [isDarkMode]
  );

  return (
    <AppRouterCacheProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </AppRouterCacheProvider>
  );
}
