'use client';

import { useEffect, useState } from 'react';
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
  Radio,
  RadioGroup,
  FormControlLabel,
  FormLabel,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  HelpOutline,
  Send,
} from '@mui/icons-material';
import { api } from '@/lib/api';

const METRIC_DESCRIPTIONS = {
  aislamiento: {
    title: 'Aislamiento en tiempos libres',
    description: '¿El alumno ha pasado el recreo o los tiempos muertos solo, o deambulando sin interactuar?',
    examples: [
      '0: Interactúa normalmente con compañeros',
      '1: Una vez se quedó solo brevemente',
      '2: Varias veces evitó grupos o estuvo solo',
      '3: Constantemente aislado, evita todo contacto'
    ]
  },
  exclusion: {
    title: 'Exclusión entre pares',
    description: '¿Ha sido rechazado explícitamente al formar grupos o nadie ha querido sentarse a su lado?',
    examples: [
      '0: Integrado en grupos sin problemas',
      '1: Una vez notó rechazo leve',
      '2: Varias veces excluido de grupos',
      '3: Rechazo constante y explícito'
    ]
  },
  reactividad: {
    title: 'Reactividad emocional inusual',
    description: '¿Ha mostrado irritabilidad desproporcionada, llanto repentino o una actitud defensiva (sobresaltos) ante acercamientos normales?',
    examples: [
      '0: Reacciones emocionales apropiadas',
      '1: Una reacción exagerada puntual',
      '2: Varias reacciones desproporcionadas',
      '3: Constantemente irritable o asustado'
    ]
  },
  inhibicion: {
    title: 'Silencio/Inhibición',
    description: '¿Ha evitado participar en clase más de lo habitual o su lenguaje corporal denota miedo (cabeza baja, hombros encogidos)?',
    examples: [
      '0: Participación y postura normales',
      '1: Algo más callado que de costumbre',
      '2: Claramente inhibido, postura cerrada',
      '3: Silencio total, lenguaje corporal de miedo'
    ]
  },
  desenganche: {
    title: 'Desenganche Escolar',
    description: '¿Presenta una bajada brusca de rendimiento (notas/tareas) O un patrón de asistencia irregular (retrasos/novillos/peticiones de salir)?',
    examples: [
      '0: Rendimiento y asistencia normales',
      '1: Leve bajada de rendimiento o asistencia irregular ocasional',
      '2: Bajada notable de rendimiento o ausencias/retrasos frecuentes',
      '3: Desenganche severo, rendimiento muy bajo o absentismo'
    ]
  },
  fisico: {
    title: 'Estado físico/material',
    description: '¿Presenta deterioro en su material (libros rotos, estuche perdido) o en su vestimenta/higiene?',
    examples: [
      '0: Material y aspecto en buen estado',
      '1: Un objeto dañado puntualmente',
      '2: Varios objetos dañados o aspecto descuidado',
      '3: Deterioro constante, vestimenta rota'
    ]
  },
  intuicion: {
    title: 'Percepción subjetiva del docente (Intuición)',
    description: 'Del 0 al 3, ¿cuánto te "preocupa" este alumno hoy basándote en tu experiencia, aunque no sepas explicar por qué?',
    examples: [
      '0: No me preocupa en absoluto',
      '1: Algo me llama la atención',
      '2: Me preocupa, debería vigilarlo',
      '3: Muy preocupado, necesita atención inmediata'
    ]
  }
};

export default function TeacherReportPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Form state
  const [classes, setClasses] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedStudent, setSelectedStudent] = useState('');
  const [metrics, setMetrics] = useState({
    aislamiento: '0',
    exclusion: '0',
    reactividad: '0',
    inhibicion: '0',
    desenganche: '0',
    fisico: '0',
    intuicion: '0'
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData || userData === 'undefined') {
      router.push('/login');
      return;
    }

    try {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);

      // If admin, redirect to dashboard
      if (parsedUser.role === 'admin') {
        router.push('/dashboard');
        return;
      }

      // Load teacher's classes
      loadClasses();
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/login');
    }
  }, [router]);

  const loadClasses = async () => {
    try {
      const data = await api.teacherReports.getCourses();
      // Ordenar clases alfabéticamente
      const sortedClasses = data.sort((a, b) => a.name.localeCompare(b.name));
      setClasses(sortedClasses);
      setLoading(false);
    } catch (err) {
      console.error('Error loading classes:', err);
      setError('Error al cargar las clases');
      setLoading(false);
    }
  };

  const handleClassChange = async (event) => {
    const classId = event.target.value;
    setSelectedClass(classId);
    setSelectedStudent('');
    setStudents([]);

    if (classId) {
      try {
        const data = await api.teacherReports.getStudents(classId);
        // Ordenar estudiantes alfabéticamente
        const sortedStudents = data.sort((a, b) => a.name.localeCompare(b.name));
        setStudents(sortedStudents);
      } catch (err) {
        console.error('Error loading students:', err);
        setError('Error al cargar los estudiantes');
      }
    }
  };

  const handleStudentChange = (event) => {
    setSelectedStudent(event.target.value);
    setError('');
    setSuccess('');
  };

  const handleMetricChange = (metric, value) => {
    setMetrics(prev => ({ ...prev, [metric]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!selectedClass || !selectedStudent) {
      setError('Por favor selecciona una clase y un estudiante');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    setSubmitting(true);

    try {
      await api.teacherReports.create({
        student_id: parseInt(selectedStudent),
        disengagement: parseInt(metrics.desenganche),
        social_isolation: parseInt(metrics.aislamiento),
        peer_exclusion: parseInt(metrics.exclusion),
        emotional_reactivity: parseInt(metrics.reactividad),
        inhibition: parseInt(metrics.inhibicion),
        physical_damage: parseInt(metrics.fisico),
        intuition: parseInt(metrics.intuicion)
      });

      setSuccess('✓ Reporte enviado exitosamente');
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // Reset form
      setSelectedStudent('');
      setMetrics({
        aislamiento: '0',
        exclusion: '0',
        reactividad: '0',
        inhibicion: '0',
        desenganche: '0',
        fisico: '0',
        intuicion: '0'
      });
    } catch (err) {
      console.error('Error submitting report:', err);
      setError(err.message || 'Error al enviar el reporte. Por favor verifica tu sesión.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  if (loading || !user) {
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
          <img
            src="/escudo_escolar_logo.png"
            alt="Escudo Escolar"
            style={{ height: 40, marginRight: 16 }}
          />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Checklist Diario para Profesores
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Cerrar Sesión
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
            Checklist Diario para los Profesores
          </Typography>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Bienvenido, {user.name}. Este formulario está diseñado para que puedas completarlo en menos de 60 segundos.
          </Typography>

          {/* Scale explanation */}
          <Paper sx={{ p: 2, mb: 4, bgcolor: 'info.lighter' }}>
            <Typography variant="subtitle1" fontWeight="600" gutterBottom>
              Escala de valoración (0-3):
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 3 }}>
              <li><strong>0:</strong> No observado / Normalidad absoluta.</li>
              <li><strong>1:</strong> Leve / Ocurrió una vez de forma aislada.</li>
              <li><strong>2:</strong> Moderado / Ocurrió varias veces o con intensidad notable.</li>
              <li><strong>3:</strong> Crítico / Ocurrió frecuentemente o con intensidad alarmante.</li>
            </Box>
            <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
              Nota: Si marcas un '3' en cualquier ítem, el sistema etiquetará el caso para revisión inmediata.
            </Typography>
          </Paper>

          {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>}

          <form onSubmit={handleSubmit}>
            {/* Class and Student Selection */}
            <Box sx={{ mb: 4 }}>
              <FormControl fullWidth sx={{ mb: 3 }} required>
                <InputLabel>Clase</InputLabel>
                <Select
                  value={selectedClass}
                  onChange={handleClassChange}
                  label="Clase"
                >
                  {classes.map((cls) => (
                    <MenuItem key={cls.id} value={cls.id}>
                      {cls.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth required disabled={!selectedClass}>
                <InputLabel>Estudiante</InputLabel>
                <Select
                  value={selectedStudent}
                  onChange={handleStudentChange}
                  label="Estudiante"
                >
                  {students.map((student) => (
                    <MenuItem key={student.id} value={student.id}>
                      {student.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Section A: Social Indicators */}
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              A. Indicadores Sociales (La "Soledad")
            </Typography>

            {['aislamiento', 'exclusion'].map((metric) => (
              <MetricRadioGroup
                key={metric}
                metric={metric}
                value={metrics[metric]}
                onChange={handleMetricChange}
                description={METRIC_DESCRIPTIONS[metric]}
              />
            ))}

            <Divider sx={{ my: 3 }} />

            {/* Section B: Behavioral Indicators */}
            <Typography variant="h6" gutterBottom>
              B. Indicadores Conductuales (El "Cambio")
            </Typography>

            {['reactividad', 'inhibicion'].map((metric) => (
              <MetricRadioGroup
                key={metric}
                metric={metric}
                value={metrics[metric]}
                onChange={handleMetricChange}
                description={METRIC_DESCRIPTIONS[metric]}
              />
            ))}

            <Divider sx={{ my: 3 }} />

            {/* Section C: Disengagement Indicators */}
            <Typography variant="h6" gutterBottom>
              C. Indicadores de Desenganche (Académico y Asistencia)
            </Typography>

            {['desenganche', 'fisico'].map((metric) => (
              <MetricRadioGroup
                key={metric}
                metric={metric}
                value={metrics[metric]}
                onChange={handleMetricChange}
                description={METRIC_DESCRIPTIONS[metric]}
              />
            ))}

            <Divider sx={{ my: 3 }} />

            {/* Section D: Control Variable */}
            <Typography variant="h6" gutterBottom>
              D. Variable de Control (Contexto)
            </Typography>

            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
              Nota: Esta variable es valiosísima. A veces el cerebro humano detecta patrones subliminales
              que las preguntas anteriores no capturan. Ayuda a reducir falsos negativos.
            </Typography>

            <MetricRadioGroup
              metric="intuicion"
              value={metrics.intuicion}
              onChange={handleMetricChange}
              description={METRIC_DESCRIPTIONS.intuicion}
            />

            {/* Submit Button */}
            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={<Send />}
                disabled={submitting || !selectedClass || !selectedStudent}
                sx={{ minWidth: 200 }}
              >
                {submitting ? 'Enviando...' : 'Enviar Reporte'}
              </Button>
            </Box>
          </form>
        </Paper>
      </Container>
    </Box>
  );
}

// Component for each metric radio group
function MetricRadioGroup({ metric, value, onChange, description }) {
  const [tooltipOpen, setTooltipOpen] = useState(false);

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <FormLabel component="legend" sx={{ flexGrow: 1 }}>
          {description.description}
        </FormLabel>
        <Tooltip
          title={
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                {description.title}
              </Typography>
              {description.examples.map((example, idx) => (
                <Typography key={idx} variant="caption" display="block">
                  {example}
                </Typography>
              ))}
            </Box>
          }
          open={tooltipOpen}
          onClose={() => setTooltipOpen(false)}
          onOpen={() => setTooltipOpen(true)}
          arrow
          placement="right"
        >
          <IconButton size="small" onClick={() => setTooltipOpen(!tooltipOpen)}>
            <HelpOutline fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <RadioGroup
        row
        value={value}
        onChange={(e) => onChange(metric, e.target.value)}
        sx={{ ml: 2 }}
      >
        <FormControlLabel value="0" control={<Radio />} label="0" />
        <FormControlLabel value="1" control={<Radio />} label="1" />
        <FormControlLabel value="2" control={<Radio />} label="2" />
        <FormControlLabel
          value="3"
          control={<Radio />}
          label="3"
          sx={{ '& .MuiFormControlLabel-label': { color: 'error.main', fontWeight: 600 } }}
        />
      </RadioGroup>
    </Box>
  );
}
