'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  Typography,
  Paper,
  AppBar,
  Toolbar,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Send,
  CheckCircle,
} from '@mui/icons-material';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function WitnessReportPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [classes, setClasses] = useState([]);
  const [witnessed, setWitnessed] = useState(false);
  const [selectedClass, setSelectedClass] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const response = await fetch(`${API_URL}/reports/student/courses`);
      if (!response.ok) throw new Error('Error al cargar las clases');

      const data = await response.json();

      // Ordenar clases por nivel educativo y luego alfabéticamente
      const sortedClasses = data.sort((a, b) => {
        // Determinar el nivel educativo
        const getLevelOrder = (name) => {
          if (name.toLowerCase().includes('primaria')) return 1;
          if (name.toLowerCase().includes('eso')) return 2;
          if (name.toLowerCase().includes('bachillerato')) return 3;
          return 4;
        };

        const levelA = getLevelOrder(a.name);
        const levelB = getLevelOrder(b.name);

        if (levelA !== levelB) {
          return levelA - levelB;
        }

        // Mismo nivel, ordenar alfabéticamente
        return a.name.localeCompare(b.name);
      });

      setClasses(sortedClasses);
      setLoading(false);
    } catch (err) {
      console.error('Error loading classes:', err);
      setError('Error al cargar las clases');
      setLoading(false);
    }
  };

  const handleCheckboxChange = (event) => {
    setWitnessed(event.target.checked);
    if (!event.target.checked) {
      setSelectedClass('');
      setError('');
      setSuccess('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      const payload = {
        class_id: selectedClass === '' || selectedClass === '0' ? null : parseInt(selectedClass),
        event_date: new Date().toISOString().split('T')[0]
      };

      const response = await fetch(`${API_URL}/reports/student`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        throw new Error(errorData.detail || 'Error al enviar el reporte');
      }

      setSuccess('✓ Gracias por tu valentía. Tu reporte ha sido registrado de forma anónima.');
      setWitnessed(false);
      setSelectedClass('');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error('Error submitting report:', err);
      setError(err.message || 'Error al enviar el reporte');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
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
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Reporte de Testigo
          </Typography>
          <Button
            color="inherit"
            component={Link}
            href="/"
            sx={{
              bgcolor: 'transparent',
              '&:hover': {
                bgcolor: 'rgba(0, 0, 0, 0.15)'
              }
            }}
          >
            Volver al Inicio
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 6, mb: 4 }}>
        <Paper sx={{ p: 5 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom fontWeight="600">
              ¿Has sido testigo de Bullying?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
              Este formulario tarda solo <strong>2 segundos</strong> en completarse
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Es completamente <strong>anónimo</strong> y confidencial
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 3 }}>
              {success}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={witnessed}
                    onChange={handleCheckboxChange}
                    sx={{
                      '& .MuiSvgIcon-root': { fontSize: 48 }
                    }}
                  />
                }
                label={
                  <Typography variant="h6">
                    Sí, he sido testigo de bullying
                  </Typography>
                }
                sx={{
                  border: '2px solid',
                  borderColor: witnessed ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 2,
                  m: 0,
                  transition: 'all 0.3s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover',
                  }
                }}
              />
            </Box>

            {witnessed && (
              <Box
                sx={{
                  animation: 'fadeIn 0.3s ease-in',
                  '@keyframes fadeIn': {
                    from: { opacity: 0, transform: 'translateY(-10px)' },
                    to: { opacity: 1, transform: 'translateY(0)' }
                  }
                }}
              >
                <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                  ¿A qué clase va la víctima?
                </Typography>

                <FormControl fullWidth sx={{ mb: 4 }}>
                  <Select
                    value={selectedClass}
                    onChange={(e) => setSelectedClass(e.target.value)}
                    displayEmpty
                    renderValue={(selected) => {
                      if (selected === '') {
                        return 'No lo sé';
                      }
                      const selectedClass = classes.find(cls => cls.id === selected);
                      return selectedClass ? selectedClass.name : 'No lo sé';
                    }}
                  >
                    <MenuItem value="">No lo sé</MenuItem>
                    {classes.map((cls) => (
                      <MenuItem key={cls.id} value={cls.id}>
                        {cls.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    startIcon={<Send />}
                    disabled={submitting}
                    sx={{
                      minWidth: 200,
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                    }}
                  >
                    {submitting ? 'Enviando...' : 'Enviar Reporte'}
                  </Button>
                </Box>
              </Box>
            )}
          </form>

          {!witnessed && !success && (
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Typography variant="body2" color="text.secondary">
                Si has presenciado una situación de bullying, tu voz es importante.
                <br />
                Marca la casilla para ayudarnos a proteger a tus compañeros.
              </Typography>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
}
