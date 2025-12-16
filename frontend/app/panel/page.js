'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Box,
  Container,
  Typography,
  Paper,
  AppBar,
  Toolbar,
  Button,
} from '@mui/material';
import { logout } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData || userData === 'undefined') {
      // Clear invalid data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/acceso');
      return;
    }

    try {
      const parsedUser = JSON.parse(userData);

      // Redirect non-admin teachers to the report form
      if (parsedUser.role !== 'admin') {
        router.push('/panel/reporte');
        return;
      }

      setUser(parsedUser);
    } catch (error) {
      // If parsing fails, clear data and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/acceso');
    }
  }, [router]);

  const handleLogout = () => {
    logout();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  if (!user) {
    return null;
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
            <img
              src="/escudo_escolar_logo.png"
              alt="Escudo Escolar"
              style={{ height: 40, marginRight: 16, cursor: 'pointer' }}
            />
          </Link>
          <Box sx={{ flexGrow: 1 }} />
          <Button
            color="inherit"
            onClick={handleLogout}
            sx={{
              bgcolor: 'transparent',
              '&:hover': {
                bgcolor: 'rgba(0, 0, 0, 0.15)'
              }
            }}
          >
            Cerrar Sesión
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom>
            Panel de Control
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Bienvenido, {user.name || user.email}
          </Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Esta es una página temporal del dashboard. Aquí podrás acceder a
            todas las funcionalidades del sistema:
          </Typography>
          <Box component="ul" sx={{ mt: 2 }}>
            <li>Ver reportes de estudiantes</li>
            <li>Gestionar alertas de bullying</li>
            <li>Analizar patrones de comportamiento</li>
            <li>Revisar estadísticas del sistema</li>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
