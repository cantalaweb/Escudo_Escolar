'use client';

import { useEffect, useState, useCallback } from 'react';
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
  ToggleButton,
  ToggleButtonGroup,
  CircularProgress,
  Alert,
  Tooltip,
  Slider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  TextField,
  FormControl,
  Select,
  MenuItem,
  IconButton,
  InputAdornment,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ReferenceArea } from 'recharts';
import { useTheme } from '@mui/material/styles';
import { logout } from '@/lib/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function DashboardPage() {
  const router = useRouter();
  const theme = useTheme();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Estado para la vista macro
  const [macroView, setMacroView] = useState('heatmap'); // 'heatmap' o 'risk-matrix'
  const [selectedStudent, setSelectedStudent] = useState(null);

  // Datos macro
  const [heatmapData, setHeatmapData] = useState(null);
  const [riskMatrixData, setRiskMatrixData] = useState(null);

  // Controles para la sección micro
  const [dataSource, setDataSource] = useState('both'); // 'teachers', 'witnesses', 'both'
  const [aiThreshold, setAiThreshold] = useState(0); // 0-100

  // Datos micro
  const [timelineData, setTimelineData] = useState(null);
  const [radarData, setRadarData] = useState(null);
  const [loadingMicro, setLoadingMicro] = useState(false);

  // Modal de detalle del día
  const [selectedDay, setSelectedDay] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Modal de gestión de casos
  const [caseModalOpen, setCaseModalOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [clickedNodeDate, setClickedNodeDate] = useState(null); // Fecha del nodo clickeado
  const [caseFormData, setCaseFormData] = useState({
    status: '',
    psychologist_notes: '',
    final_diagnosis: '',
    closed_at: null
  });

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
      loadDashboardData();
    } catch (error) {
      // If parsing fails, clear data and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/acceso');
    }
  }, [router]);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');

      // Cargar datos en paralelo para mejor rendimiento
      const [heatmapRes, riskRes] = await Promise.all([
        fetch(`${API_URL}/dashboard/heatmap?days=60`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/dashboard/risk-matrix`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (heatmapRes.ok) {
        const heatmapData = await heatmapRes.json();
        setHeatmapData(heatmapData);
      }

      if (riskRes.ok) {
        const riskData = await riskRes.json();
        setRiskMatrixData(riskData);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Error al cargar los datos del dashboard');
      setLoading(false);
    }
  };

  const loadStudentData = useCallback(async (studentId) => {
    console.log('Loading data for student:', studentId);
    setLoadingMicro(true);
    setError('');

    try {
      const token = localStorage.getItem('token');

      // Build query params
      const params = new URLSearchParams();
      if (dataSource !== 'both') {
        params.append('source', dataSource);
      }
      if (aiThreshold > 0) {
        params.append('min_probability', aiThreshold / 100);
      }

      // Load timeline
      console.log('Fetching timeline...');
      const timelineRes = await fetch(
        `${API_URL}/dashboard/student/${studentId}/timeline?${params.toString()}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (timelineRes.ok) {
        const timeline = await timelineRes.json();
        setTimelineData(timeline);
      } else {
        const errorText = await timelineRes.text();
        console.error('Timeline error:', timelineRes.status, errorText);
        setError(`Error al cargar timeline: ${timelineRes.status}`);
      }

      // Load radar
      console.log('Fetching radar...');
      const radarRes = await fetch(
        `${API_URL}/dashboard/student/${studentId}/radar`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (radarRes.ok) {
        const radar = await radarRes.json();
        console.log('Radar data:', radar);

        // Transform radar data to match chart format
        const categoryDescriptions = {
          'A_Social': 'Social (aislamiento + exclusión)',
          'B_Conductual': 'Conductual (reactividad + inhibición)',
          'C_Desenganche': 'Desenganche (desconexión + daño físico)',
          'D_Intuicion': 'Intuición del profesor'
        };

        const categories = Object.keys(radar.student_data || {}).map(key => ({
          category: key.replace('_', ': '),
          student_avg: radar.student_data[key],
          class_avg: radar.class_average[key],
          description: categoryDescriptions[key] || key
        }));

        setRadarData({ ...radar, categories });
      } else {
        const errorText = await radarRes.text();
        console.error('Radar error:', radarRes.status, errorText);
        setError(`Error al cargar radar: ${radarRes.status}`);
      }

      setLoadingMicro(false);
    } catch (err) {
      console.error('Error loading student data:', err);
      setError('Error al cargar los datos del estudiante: ' + err.message);
      setLoadingMicro(false);
    }
  }, [dataSource, aiThreshold]);

  // Load student data when selected or filters change
  useEffect(() => {
    if (selectedStudent) {
      console.log('Selected student changed to:', selectedStudent);
      loadStudentData(selectedStudent);
    } else {
      console.log('No student selected');
      setTimelineData(null);
      setRadarData(null);
    }
  }, [selectedStudent, loadStudentData]);

  const handleLogout = () => {
    logout();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  const handleNodeClick = (data) => {
    if (data && data.case) {
      setClickedNodeDate(data.date); // Guardar fecha del nodo clickeado
      setSelectedCase(data.case);
      setCaseFormData({
        status: data.case.status || '',
        psychologist_notes: data.case.psychologist_notes || '',
        final_diagnosis: data.case.final_diagnosis || '',
        closed_at: data.case.closed_at || null
      });
      setCaseModalOpen(true);
    }
  };

  const handleCaseUpdate = async () => {
    if (!selectedCase) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/dashboard/case/${selectedCase.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(caseFormData)
      });

      if (response.ok) {
        // Recargar datos del estudiante para reflejar los cambios
        if (selectedStudent) {
          loadStudentData(selectedStudent);
        }
        setCaseModalOpen(false);
      } else {
        console.error('Error updating case:', response.status);
      }
    } catch (err) {
      console.error('Error updating case:', err);
    }
  };

  const handleCreateCase = async (nodeDate) => {
    if (!selectedStudent || !timelineData) {
      console.error('Missing data:', { selectedStudent, timelineData });
      alert('Error: Datos incompletos. Por favor, recarga la página.');
      return;
    }

    // Confirmar con el usuario
    if (!confirm('¿Deseas crear un nuevo caso para este día?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');

      // 1. Encontrar todos los casos del estudiante ordenados por fecha de apertura
      const allCasesInTimeline = timelineData.timeline
        .map(day => day.case)
        .filter(c => c !== null);

      // Eliminar duplicados por case.id
      const uniqueCases = Array.from(
        new Map(allCasesInTimeline.map(c => [c.id, c])).values()
      ).sort((a, b) => new Date(a.opened_at) - new Date(b.opened_at));

      // 2. Encontrar el siguiente caso después de la fecha del nodo clickeado
      const nextCase = uniqueCases.find(c => new Date(c.opened_at) > new Date(nodeDate));

      // 3. Calcular closed_at
      let closedAt = null;

      if (nextCase) {
        // Hay un caso posterior: encontrar el último nodo antes de que comience
        const nodesBeforeNextCase = timelineData.timeline
          .filter(day => {
            const dayDate = new Date(day.date);
            return dayDate >= new Date(nodeDate) && dayDate < new Date(nextCase.opened_at);
          })
          .sort((a, b) => new Date(b.date) - new Date(a.date));

        if (nodesBeforeNextCase.length > 0) {
          closedAt = nodesBeforeNextCase[0].date;
        } else {
          // No hay nodos entre este y el siguiente caso
          closedAt = nodeDate;
        }
      }
      // Si no hay caso posterior, closedAt se queda null (caso abierto)

      const payload = {
        student_id: timelineData.student_id,
        opened_at: nodeDate,
        closed_at: closedAt
      };

      console.log('Creating case with payload:', payload);
      console.log('Timeline data:', timelineData);

      // 4. Crear el caso
      const response = await fetch(`${API_URL}/dashboard/case`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        // Recargar datos del estudiante
        loadStudentData(selectedStudent);
        alert('Caso creado exitosamente');
      } else {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        console.error('Error creating case:', response.status, errorData);

        // Formatear el mensaje de error
        let errorMsg = `Error ${response.status}`;
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMsg += `: ${errorData.detail}`;
          } else if (Array.isArray(errorData.detail)) {
            // Errores de validación de Pydantic
            errorMsg += ':\n' + errorData.detail.map(err =>
              `- ${err.loc?.join('.')||'campo'}: ${err.msg}`
            ).join('\n');
          } else {
            errorMsg += `: ${JSON.stringify(errorData.detail)}`;
          }
        }

        alert(`Error al crear el caso:\n${errorMsg}`);
      }
    } catch (err) {
      console.error('Error creating case:', err);
      alert(`Error al crear el caso: ${err.message || JSON.stringify(err)}`);
    }
  };

  if (loading || !user) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
            <img
              src="/escudo_escolar_logo.png"
              alt="Escudo Escolar"
              style={{ height: 40, marginRight: 16, cursor: 'pointer' }}
            />
          </Link>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Dashboard de Coordinación
          </Typography>
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

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* SECCIÓN MACRO */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" fontWeight="600">
              Visión Global del Colegio
            </Typography>

            <ToggleButtonGroup
              value={macroView}
              exclusive
              onChange={(e, value) => value && setMacroView(value)}
              size="small"
            >
              <ToggleButton value="heatmap">
                Mapa de Calor
              </ToggleButton>
              <ToggleButton value="risk-matrix">
                Matriz de Riesgo
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Vista de Mapa de Calor */}
          {macroView === 'heatmap' && heatmapData && (
            <Box sx={{ minHeight: 400 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Mostrando alumnos con reportes desde {heatmapData.start_date} hasta {heatmapData.end_date}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                {heatmapData.students.length} estudiantes con incidencias
              </Typography>

              {/* Heatmap Grid */}
              <Box sx={{ mt: 2, overflowX: 'auto', maxWidth: '100%' }}>
                <Box sx={{ display: 'inline-block', minWidth: 'max-content' }}>
                  {/* Header with dates */}
                  <Box sx={{ display: 'flex', mb: 1 }}>
                    <Box sx={{ width: 200, flexShrink: 0 }} /> {/* Space for student names */}
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {(() => {
                        const start = new Date(heatmapData.start_date);
                        const end = new Date(heatmapData.end_date);
                        const days = [];
                        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
                          days.push(new Date(d));
                        }

                        // Generar etiquetas de meses con separadores verticales
                        const monthLabels = [];
                        let currentMonth = null;

                        days.forEach((date, idx) => {
                          const month = date.getMonth();
                          const isNewMonth = currentMonth !== null && month !== currentMonth;
                          const isFirstDay = idx === 0;

                          if (isFirstDay || isNewMonth) {
                            currentMonth = month;
                            const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                              'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                            monthLabels.push({
                              index: idx,
                              label: monthNames[month],
                              isFirst: isFirstDay
                            });
                          } else {
                            currentMonth = month;
                          }
                        });

                        return days.map((date, idx) => {
                          const monthLabel = monthLabels.find(m => m.index === idx);

                          return (
                            <Box
                              key={idx}
                              sx={{
                                width: 16,
                                height: 16,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'flex-start',
                                fontSize: '8px',
                                color: 'text.secondary',
                                position: 'relative'
                              }}
                              title={date.toLocaleDateString('es-ES')}
                            >
                              {monthLabel && (
                                <Box sx={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 0.25,
                                  whiteSpace: 'nowrap',
                                  position: 'absolute',
                                  left: 0,
                                  top: 0
                                }}>
                                  {!monthLabel.isFirst && <span>|</span>}
                                  <span>{monthLabel.label}</span>
                                </Box>
                              )}
                            </Box>
                          );
                        });
                      })()}
                    </Box>
                  </Box>

                  {/* Student rows */}
                  {heatmapData.students.map((student) => {
                    const start = new Date(heatmapData.start_date);
                    const end = new Date(heatmapData.end_date);
                    const days = [];
                    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
                      days.push(new Date(d).toISOString().split('T')[0]);
                    }

                    return (
                      <Box
                        key={student.student_id}
                        sx={{
                          display: 'flex',
                          mb: 0.5,
                          '&:hover': {
                            '& .student-name': {
                              bgcolor: 'action.hover',
                            }
                          }
                        }}
                      >
                        {/* Student name */}
                        <Box
                          className="student-name"
                          sx={{
                            width: 200,
                            flexShrink: 0,
                            pr: 2,
                            display: 'flex',
                            alignItems: 'center',
                            cursor: 'pointer',
                            borderRadius: 1,
                            transition: 'background-color 0.2s',
                          }}
                          onClick={() => setSelectedStudent(student.student_id)}
                          title={student.class_name}
                        >
                          <Typography variant="body2" sx={{ fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {student.student_name}
                          </Typography>
                        </Box>

                        {/* Day cells */}
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {days.map((date, idx) => {
                            const dayData = student.daily_data[date];
                            const severity = dayData?.severity || 0;

                            // Color scale: adapted for light/dark mode
                            const colors = [
                              theme.palette.mode === 'dark' ? '#424242' : '#ebedf0',  // 0 - no reports
                              '#ffcccc',  // 1 - low
                              '#ff9999',  // 2 - medium
                              '#ff6666',  // 3 - high (or higher)
                            ];
                            const bgColor = severity > 0 ? colors[Math.min(severity, 3)] : colors[0];

                            return (
                              <Box
                                key={idx}
                                sx={{
                                  width: 16,
                                  height: 16,
                                  bgcolor: bgColor,
                                  borderRadius: 0.5,
                                  border: '1px solid rgba(0,0,0,0.05)',
                                  cursor: dayData ? 'pointer' : 'default',
                                  transition: 'all 0.2s',
                                  '&:hover': dayData ? {
                                    transform: 'scale(1.2)',
                                    boxShadow: 1,
                                    zIndex: 10,
                                  } : {}
                                }}
                                title={dayData ? `${date}\n${dayData.count} reporte(s)\nSeveridad: ${severity}` : date}
                                onClick={() => {
                                  if (dayData) {
                                    setSelectedStudent(student.student_id);
                                  }
                                }}
                              />
                            );
                          })}
                        </Box>
                      </Box>
                    );
                  })}

                  {/* Legend */}
                  <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1, ml: '200px' }}>
                    <Typography variant="caption" color="text.secondary">Menos</Typography>
                    <Box sx={{ width: 16, height: 16, bgcolor: theme.palette.mode === 'dark' ? '#424242' : '#ebedf0', borderRadius: 0.5, border: '1px solid rgba(0,0,0,0.05)' }} />
                    <Box sx={{ width: 16, height: 16, bgcolor: '#ffcccc', borderRadius: 0.5 }} />
                    <Box sx={{ width: 16, height: 16, bgcolor: '#ff9999', borderRadius: 0.5 }} />
                    <Box sx={{ width: 16, height: 16, bgcolor: '#ff6666', borderRadius: 0.5 }} />
                    <Typography variant="caption" color="text.secondary">Más</Typography>
                  </Box>
                </Box>
              </Box>
            </Box>
          )}

          {/* Vista de Matriz de Riesgo */}
          {macroView === 'risk-matrix' && riskMatrixData && (
            <Box sx={{ minHeight: 400 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Distribución de estudiantes por número de reportes y probabilidad de riesgo
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                {riskMatrixData.students.length} estudiantes evaluados
              </Typography>

              {/* Scatter Plot */}
              <Box sx={{ mt: 3, width: '100%', height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart
                    margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
                    onClick={(data) => {
                      console.log('ScatterChart clicked:', data);
                      if (data && data.activeIndex !== undefined && riskMatrixData?.students) {
                        const index = parseInt(data.activeIndex);
                        const studentData = riskMatrixData.students[index];
                        console.log('Student data from scatter:', studentData);
                        if (studentData) {
                          setSelectedStudent(studentData.student_id);
                          setTimeout(() => {
                            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                          }, 100);
                        }
                      }
                    }}
                  >
                    <defs>
                      <linearGradient id="dangerGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ff5252" stopOpacity={1.0} />
                        <stop offset="100%" stopColor="#ff5252" stopOpacity={0.15} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <ReferenceArea y1={71} y2={100} fill="url(#dangerGradient)" />
                    <XAxis
                      type="number"
                      dataKey="report_count"
                      name="Reportes"
                      label={{ value: 'Número de Reportes', position: 'insideBottom', offset: -10 }}
                      domain={[0, 'auto']}
                    />
                    <YAxis
                      type="number"
                      dataKey="bullying_probability"
                      name="Probabilidad"
                      label={{ value: 'Probabilidad de Bullying (%)', angle: -90, position: 'insideLeft', offset: 10 }}
                      domain={[0, 100]}
                    />
                    <RechartsTooltip
                      cursor={{ strokeDasharray: '3 3' }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <Paper sx={{ p: 1.5, boxShadow: 3 }}>
                              <Typography variant="body2" fontWeight="600">
                                {data.student_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {data.class_name}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" display="block">
                                  Reportes: {data.report_count}
                                </Typography>
                                <Typography variant="caption" display="block">
                                  Riesgo: {data.bullying_probability}%
                                </Typography>
                              </Box>
                            </Paper>
                          );
                        }
                        return null;
                      }}
                    />
                    <Scatter
                      data={riskMatrixData.students}
                      fill="#8884d8"
                      shape="circle"
                      style={{ cursor: 'pointer' }}
                    >
                      {riskMatrixData.students.map((student, index) => {
                        // Color based on risk level
                        let color = '#4caf50'; // green - low risk
                        if (student.bullying_probability >= 70) {
                          color = '#f44336'; // red - high risk
                        } else if (student.bullying_probability >= 40) {
                          color = '#ff9800'; // orange - medium risk
                        }

                        return (
                          <Cell
                            key={`cell-${index}`}
                            fill={color}
                          />
                        );
                      })}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </Box>

              {/* Legend */}
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, bgcolor: '#4caf50', borderRadius: '50%' }} />
                  <Typography variant="caption">Bajo (&lt;40%)</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, bgcolor: '#ff9800', borderRadius: '50%' }} />
                  <Typography variant="caption">Medio (40-70%)</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, bgcolor: '#f44336', borderRadius: '50%' }} />
                  <Typography variant="caption">Alto (&gt;70%)</Typography>
                </Box>
              </Box>
            </Box>
          )}
        </Paper>

        {/* BARRA DE CONTROLES */}
        {selectedStudent && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', gap: 4, alignItems: 'center', flexWrap: 'wrap' }}>
              {/* Source Toggle */}
              <Box sx={{ flex: '0 0 auto' }}>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                  Fuente de Datos
                </Typography>
                <ToggleButtonGroup
                  value={dataSource}
                  exclusive
                  onChange={(e, value) => value && setDataSource(value)}
                  size="small"
                >
                  <ToggleButton value="teachers">
                    Solo Profesores
                  </ToggleButton>
                  <ToggleButton value="witnesses">
                    Solo Testigos
                  </ToggleButton>
                  <ToggleButton value="both">
                    Profesores + Testigos
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>

              {/* AI Threshold Slider */}
              <Box sx={{ flex: '1 1 300px', minWidth: 200 }}>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                  Umbral de Confianza IA: {aiThreshold}%
                </Typography>
                <Slider
                  value={aiThreshold}
                  onChange={(e, value) => setAiThreshold(value)}
                  min={0}
                  max={100}
                  step={5}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 50, label: '50%' },
                    { value: 100, label: '100%' }
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>
            </Box>
          </Paper>
        )}

        {/* SECCIÓN MICRO */}
        {selectedStudent && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ mb: 2, p: 2, bgcolor: 'action.selected', borderRadius: 1 }}>
              <Typography variant="body2">
                Estudiante seleccionado: ID {selectedStudent}
                {(() => {
                  // Find student name from heatmap or risk matrix data
                  let studentName = '';
                  if (heatmapData) {
                    const student = heatmapData.students.find(s => s.student_id === selectedStudent);
                    if (student) studentName = ` - ${student.student_name}`;
                  }
                  if (!studentName && riskMatrixData) {
                    const student = riskMatrixData.students.find(s => s.student_id === selectedStudent);
                    if (student) studentName = ` - ${student.student_name}`;
                  }
                  return studentName;
                })()}
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {loadingMicro ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' }, overflow: 'hidden' }}>
                {/* Timeline (75% width) */}
                <Box sx={{ flex: '3 1 0', minWidth: 0 }}>
                  <Typography variant="h6" fontWeight="600" gutterBottom>
                    Línea Temporal de Riesgo
                  </Typography>

                  {timelineData && timelineData.timeline && timelineData.timeline.length > 0 ? (
                    <Box sx={{
                      mt: 2,
                      overflowX: 'auto',
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      p: 1,
                      '&::-webkit-scrollbar': {
                        height: '8px',
                      },
                      '&::-webkit-scrollbar-track': {
                        background: '#f1f1f1',
                      },
                      '&::-webkit-scrollbar-thumb': {
                        background: '#888',
                        borderRadius: '4px',
                      },
                      '&::-webkit-scrollbar-thumb:hover': {
                        background: '#555',
                      },
                    }}>
                      <LineChart
                        width={Math.max(1500, timelineData.timeline.length * 50)}
                        height={400}
                        data={timelineData.timeline}
                        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                      >
                            <defs>
                              <linearGradient id="dangerGradientTimeline" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#ff5252" stopOpacity={1.0} />
                                <stop offset="100%" stopColor="#ff5252" stopOpacity={0.15} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                            <ReferenceArea y1={0.71} y2={1.0} fill="url(#dangerGradientTimeline)" />
                            <XAxis
                              dataKey="date"
                              angle={-45}
                              textAnchor="end"
                              height={80}
                              tick={{ fontSize: 12 }}
                            />
                            <YAxis
                              domain={[0, 1]}
                              label={{ value: 'Probabilidad de Bullying', angle: -90, position: 'insideLeft' }}
                            />
                            <RechartsTooltip content={<div />} />
                            <Line
                              type="monotone"
                              dataKey={(data) => data.ai_prediction?.bullying_probability || 0}
                              stroke="#9e9e9e"
                              strokeWidth={2}
                              dot={(props) => {
                                const { cx, cy, payload } = props;
                                if (!payload) return null;

                                const node = payload;

                                // Calculate radius based on total_severity (logarithmic scale)
                                const totalSeverity = node.total_severity || 0;
                                const radius = Math.max(8, Math.min(30, 8 + Math.log(totalSeverity + 1) * 5));

                                // Category colors
                                const categoryColors = {
                                  'A': '#ff6b6b',  // Red - Social
                                  'B': '#4ecdc4',  // Teal - Conductual
                                  'C': '#ffe66d',  // Yellow - Desenganche
                                  'D': '#a8dadc',  // Light blue - Intuición
                                };

                                const coreColor = categoryColors[node.dominant_category] || '#9e9e9e';
                                const activeCount = node.active_categories_count || 0;

                                // Determine border
                                const borderColor = activeCount > 1 ? '#555555' : coreColor;
                                const borderStyle = activeCount > 1 ? '3 3' : '0';

                                return (
                                  <g>
                                    {/* Outer border/halo */}
                                    <circle
                                      cx={cx}
                                      cy={cy}
                                      r={radius}
                                      fill="none"
                                      stroke={borderColor}
                                      strokeWidth={activeCount > 1 ? 3 : 2}
                                      strokeDasharray={borderStyle}
                                      style={{ cursor: 'pointer' }}
                                      onClick={() => {
                                        if (node.case) {
                                          handleNodeClick(node);
                                        } else {
                                          handleCreateCase(node.date);
                                        }
                                      }}
                                    />
                                    {/* Core */}
                                    <circle
                                      cx={cx}
                                      cy={cy}
                                      r={radius - 4}
                                      fill={coreColor}
                                      opacity={0.8}
                                      style={{ cursor: 'pointer' }}
                                      onClick={() => {
                                        if (node.case) {
                                          handleNodeClick(node);
                                        } else {
                                          handleCreateCase(node.date);
                                        }
                                      }}
                                    />
                                  </g>
                                );
                              }}
                            />
                          </LineChart>

                        {/* Legend for categories */}
                        <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Box sx={{ width: 16, height: 16, bgcolor: '#ff6b6b', borderRadius: '50%' }} />
                          <Typography variant="caption">A: Social</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Box sx={{ width: 16, height: 16, bgcolor: '#4ecdc4', borderRadius: '50%' }} />
                          <Typography variant="caption">B: Conductual</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Box sx={{ width: 16, height: 16, bgcolor: '#ffe66d', borderRadius: '50%' }} />
                          <Typography variant="caption">C: Desenganche</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Box sx={{ width: 16, height: 16, bgcolor: '#a8dadc', borderRadius: '50%' }} />
                          <Typography variant="caption">D: Intuición</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Box sx={{ width: 16, height: 16, border: '3px dotted #555555', borderRadius: '50%' }} />
                          <Typography variant="caption">Multicausal</Typography>
                        </Box>
                      </Box>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      No hay datos de línea temporal para este estudiante
                    </Typography>
                  )}
                </Box>

                {/* Radar Chart (25% width) */}
                <Box sx={{ flex: '1 1 0', minWidth: 250 }}>
                  <Typography variant="h6" fontWeight="600" gutterBottom>
                    Perfil del Estudiante
                  </Typography>

                  {radarData && radarData.categories && radarData.categories.length > 0 ? (
                    <Box sx={{ mt: 2, height: 350 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={radarData.categories}>
                          <PolarGrid stroke="#e0e0e0" />
                          <PolarAngleAxis dataKey="category" tick={{ fontSize: 12 }} />
                          <PolarRadiusAxis angle={90} domain={[0, 3]} tick={{ fontSize: 10 }} />
                          <Radar
                            name="Alumno"
                            dataKey="student_avg"
                            stroke="#2196f3"
                            fill="#2196f3"
                            fillOpacity={0.5}
                          />
                          <Radar
                            name="Media Clase"
                            dataKey="class_avg"
                            stroke="#9e9e9e"
                            fill="#9e9e9e"
                            fillOpacity={0.25}
                          />
                          <Legend />
                        </RadarChart>
                      </ResponsiveContainer>

                      <Box sx={{ mt: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                          Categorías
                        </Typography>
                        {radarData.categories.map((cat) => (
                          <Typography key={cat.category} variant="caption" display="block">
                            {cat.category}: {cat.description}
                          </Typography>
                        ))}
                      </Box>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      No hay datos de perfil para este estudiante
                    </Typography>
                  )}
                </Box>
              </Box>
            )}
          </Paper>
        )}

        {!selectedStudent && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              Selecciona un estudiante en la vista superior para ver su perfil detallado
            </Typography>
          </Paper>
        )}

        {/* MODAL DE DETALLE DEL DÍA */}
        <Dialog
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            Detalle del Día: {selectedDay?.date}
          </DialogTitle>
          <DialogContent>
            {selectedDay && (
              <Box>
                <Typography variant="body2" gutterBottom>
                  <strong>Probabilidad de Bullying:</strong> {selectedDay.ai_prediction ? (selectedDay.ai_prediction.bullying_probability * 100).toFixed(1) + '%' : 'N/A'}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Categoría Dominante:</strong> {selectedDay.dominant_category || 'N/A'}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Total de Severidad:</strong> {selectedDay.total_severity || 0}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom>
                  Reportes del Día
                </Typography>

                {/* Teacher Reports */}
                {selectedDay.teacher_reports && selectedDay.teacher_reports.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Reportes de Profesores ({selectedDay.teacher_reports.length})
                    </Typography>
                    {selectedDay.teacher_reports.map((report, idx) => (
                      <Paper key={idx} sx={{ p: 2, mb: 1, bgcolor: 'action.hover' }}>
                        <Typography variant="body2">
                          <strong>Profesor:</strong> {report.teacher_name}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Asignatura:</strong> {report.subject_name || 'N/A'}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          Métricas: Social Isolation ({report.metrics?.social_isolation || 0}),
                          Peer Exclusion ({report.metrics?.peer_exclusion || 0}),
                          Emotional Reactivity ({report.metrics?.emotional_reactivity || 0}),
                          Inhibition ({report.metrics?.inhibition || 0}),
                          Disengagement ({report.metrics?.disengagement || 0}),
                          Physical Damage ({report.metrics?.physical_damage || 0}),
                          Intuition ({report.metrics?.intuition || 0})
                        </Typography>
                      </Paper>
                    ))}
                  </Box>
                )}

                {/* Witness Report Count */}
                {selectedDay.witness_report_count > 0 && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Reportes de Testigos
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'action.hover' }}>
                      <Typography variant="body2">
                        {selectedDay.witness_report_count} reporte(s) anónimo(s) de testigos en esta clase
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {selectedDay.teacher_reports?.length === 0 && selectedDay.witness_report_count === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    No hay reportes registrados para este día
                  </Typography>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setModalOpen(false)}>Cerrar</Button>
          </DialogActions>
        </Dialog>

        {/* Modal de Gestión de Casos */}
        <Dialog
          open={caseModalOpen}
          onClose={() => setCaseModalOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            Gestión de Caso
            {selectedCase && (
              <Typography variant="body2" color="text.secondary">
                Caso #{selectedCase.id} - Abierto el {selectedCase.opened_at}
              </Typography>
            )}
          </DialogTitle>
          <DialogContent>
            {selectedCase && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                {/* Estado del caso */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Estado del Caso
                  </Typography>
                  <FormControl fullWidth>
                    <Select
                      value={caseFormData.status || ''}
                      onChange={(e) => setCaseFormData({ ...caseFormData, status: e.target.value })}
                      displayEmpty
                    >
                      <MenuItem value="">Sin estado</MenuItem>
                      <MenuItem value="INVESTIGATING">Investigando</MenuItem>
                      <MenuItem value="CONFIRMED">Confirmado</MenuItem>
                      <MenuItem value="FALSE_ALARM">Falsa Alarma</MenuItem>
                      <MenuItem value="RESOLVED">Resuelto</MenuItem>
                      <MenuItem value="MONITORING">Monitoreando</MenuItem>
                    </Select>
                  </FormControl>
                </Box>

                {/* Notas del psicólogo */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Notas del Psicólogo
                  </Typography>
                  <TextField
                    multiline
                    rows={4}
                    fullWidth
                    value={caseFormData.psychologist_notes || ''}
                    onChange={(e) => setCaseFormData({ ...caseFormData, psychologist_notes: e.target.value })}
                    placeholder="Escribe las observaciones del psicólogo..."
                  />
                </Box>

                {/* Diagnóstico final */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Diagnóstico Final
                  </Typography>
                  <TextField
                    fullWidth
                    value={caseFormData.final_diagnosis || ''}
                    onChange={(e) => setCaseFormData({ ...caseFormData, final_diagnosis: e.target.value })}
                    placeholder="Ej: Conflicto puntual, Acoso escolar, Problema familiar..."
                  />
                </Box>

                {/* Estado del caso */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Estado del Caso
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={!caseFormData.closed_at}
                        onChange={(e) => {
                          // Usar la fecha del nodo clickeado
                          setCaseFormData({
                            ...caseFormData,
                            closed_at: e.target.checked ? null : clickedNodeDate
                          });
                        }}
                        color="primary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body1">
                          {caseFormData.closed_at ? 'Cerrado' : 'Abierto'}
                        </Typography>
                        {caseFormData.closed_at && (
                          <Typography variant="caption" color="text.secondary">
                            Fecha de cierre: {caseFormData.closed_at}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </Box>

                {/* Información del caso */}
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Información del Caso
                  </Typography>
                  <Typography variant="body2">
                    <strong>Fecha de Apertura:</strong> {selectedCase.opened_at}
                  </Typography>
                  {selectedCase.closed_at && (
                    <Typography variant="body2">
                      <strong>Fecha de Cierre:</strong> {selectedCase.closed_at}
                    </Typography>
                  )}
                </Box>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCaseModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleCaseUpdate} variant="contained" color="primary">
              Guardar Cambios
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
