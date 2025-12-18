/**
 * API Client para conectar con el backend FastAPI de Escudo Escolar
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Wrapper genérico para fetch con manejo de errores
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Error desconocido',
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Obtener token de localStorage
 */
function getToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

/**
 * Guardar token en localStorage
 */
export function setToken(token) {
  localStorage.setItem('token', token);
}

/**
 * Eliminar token de localStorage
 */
export function removeToken() {
  localStorage.removeItem('token');
}

/**
 * Fetch con autenticación
 */
async function fetchWithAuth(endpoint, options = {}) {
  const token = getToken();

  if (!token) {
    throw new Error('No estás autenticado');
  }

  return fetchAPI(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
}

// =============================================================================
// MÉTODOS DE LA API
// =============================================================================

export const api = {
  // Health Check
  health: () => fetchAPI('/api/health'),

  // Autenticación
  auth: {
    login: (email, password) =>
      fetchAPI('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    logout: () => {
      removeToken();
    },
  },

  // Reportes de Testigos (Estudiantes)
  witnessReports: {
    getCourses: () => fetchAPI('/reports/student/courses'),

    create: (classId, eventDate) =>
      fetchAPI('/reports/student', {
        method: 'POST',
        body: JSON.stringify({
          class_id: classId,
          event_date: eventDate,
        }),
      }),
  },

  // Reportes de Profesores
  teacherReports: {
    getCourses: () => fetchWithAuth('/reports/teacher/courses'),

    getStudents: (classId) =>
      fetchWithAuth(`/reports/teacher/students/${classId}`),

    create: (data) =>
      fetchWithAuth('/reports/teacher', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Chatbot (Alex - Multi-agent support system)
  chatbot: {
    send: (message, threadId) =>
      fetchAPI('/api/chatbot', {
        method: 'POST',
        body: JSON.stringify({ message, thread_id: threadId }),
      }),

    health: () => fetchAPI('/api/chatbot/health'),
  },

  // Features (para ML)
  features: {
    getStudent: (studentId) => fetchAPI(`/reports/features/${studentId}`),
  },
};

// Export convenience functions
export const login = api.auth.login;
export const logout = api.auth.logout;
