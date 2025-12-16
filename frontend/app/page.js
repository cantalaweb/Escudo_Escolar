'use client';

import Link from 'next/link';
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  Chat,
  Assessment,
  Security,
} from '@mui/icons-material';

export default function Home() {
  return (
    <Box>
      {/* Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <img
            src="/escudo_escolar_logo.png"
            alt="Escudo Escolar Logo"
            style={{ height: 40, marginRight: 16 }}
          />
          <Box sx={{ flexGrow: 1 }} />
          <Button color="inherit" component={Link} href="/login">
            Iniciar Sesión
          </Button>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 12,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
            Sistema de Detección Temprana de Bullying
          </Typography>
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
            Protegiendo a nuestros estudiantes con inteligencia artificial
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              color="secondary"
              component={Link}
              href="/login"
            >
              Acceso Profesores
            </Button>
            <Button
              variant="outlined"
              size="large"
              sx={{ borderColor: 'white', color: 'white' }}
              component={Link}
              href="/chat"
            >
              Chatbot de Apoyo
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h3" align="center" gutterBottom sx={{ mb: 6 }}>
          Características Principales
        </Typography>

        <Grid container spacing={4}>
          {/* Feature 1 */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Assessment
                  sx={{ fontSize: 60, color: 'primary.main', mb: 2 }}
                />
                <Typography variant="h5" gutterBottom>
                  Detección Temprana
                </Typography>
                <Typography color="text.secondary">
                  Algoritmos de IA para identificar patrones de comportamiento
                  preocupantes antes de que escalen
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Feature 2 */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Chat sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  Chatbot de Apoyo
                </Typography>
                <Typography color="text.secondary">
                  Asistente virtual disponible 24/7 para estudiantes que
                  necesiten hablar o reportar situaciones
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Feature 3 */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Security
                  sx={{ fontSize: 60, color: 'success.main', mb: 2 }}
                />
                <Typography variant="h5" gutterBottom>
                  Reportes Seguros
                </Typography>
                <Typography color="text.secondary">
                  Sistema de reportes confidenciales para estudiantes y
                  profesores con total privacidad
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ bgcolor: 'grey.100', py: 8 }}>
        <Container maxWidth="md">
          <Typography variant="h4" align="center" gutterBottom>
            ¿Eres profesor o administrador?
          </Typography>
          <Typography
            variant="body1"
            align="center"
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            Accede al sistema para gestionar reportes y monitorear el bienestar
            de tus estudiantes
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              component={Link}
              href="/login"
            >
              Iniciar Sesión
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{ bgcolor: 'grey.900', color: 'white', py: 4 }}
      >
        <Container>
          <Typography variant="body2" align="center">
            Escudo Escolar v2.0 - Sistema de Detección de Bullying con IA
          </Typography>
          <Typography variant="caption" align="center" display="block">
            Protegiendo a nuestros estudiantes
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
