'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Box,
  Container,
  Paper,
  TextField,
  IconButton,
  Typography,
  AppBar,
  Toolbar,
  Avatar,
  CircularProgress,
} from '@mui/material';
import {
  Send,
  ArrowBack,
  SmartToy,
  Person,
} from '@mui/icons-material';
import { api } from '@/lib/api';

// Generar un ID único para la sesión
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
};

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);

  // Generar o recuperar session ID desde sessionStorage
  useEffect(() => {
    // Intentar recuperar sessionId existente
    let existingSessionId = null;
    if (typeof window !== 'undefined') {
      existingSessionId = sessionStorage.getItem('chatSessionId');
    }

    // Si no existe, generar uno nuevo y guardarlo
    if (!existingSessionId) {
      existingSessionId = generateSessionId();
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('chatSessionId', existingSessionId);
      }
    }

    setSessionId(existingSessionId);

    // Mensaje de bienvenida
    setMessages([{
      role: 'assistant',
      content: 'Hola, soy Alex, tu compañero virtual. Estoy aquí para escucharte y acompañarte. ¿Cómo te sientes hoy?',
      timestamp: new Date(),
    }]);
  }, []);

  // Auto-scroll al final
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const data = await api.chatbot.send(input, sessionId);

      const assistantMessage = {
        role: 'assistant',
        content: data.respuesta,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);

      const errorMessage = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            component={Link}
            href="/"
            sx={{ mr: 2 }}
          >
            <ArrowBack />
          </IconButton>

          <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
            <SmartToy />
          </Avatar>

          <Box>
            <Typography variant="h6" component="div">
              Alex
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              Tu compañero virtual de apoyo
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          bgcolor: 'action.hover',
        }}
      >
        <Container maxWidth="md">
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              {message.role === 'assistant' && (
                <Avatar
                  sx={{
                    bgcolor: 'secondary.main',
                    mr: 1,
                    width: 32,
                    height: 32,
                  }}
                >
                  <SmartToy fontSize="small" />
                </Avatar>
              )}

              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: message.role === 'user' ? 'primary.main' : 'background.paper',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  borderRadius: 2,
                }}
              >
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {message.content}
                </Typography>

                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 0.5,
                    opacity: 0.7,
                    textAlign: 'right',
                  }}
                >
                  {message.timestamp.toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Typography>
              </Paper>

              {message.role === 'user' && (
                <Avatar
                  sx={{
                    bgcolor: 'grey.500',
                    ml: 1,
                    width: 32,
                    height: 32,
                  }}
                >
                  <Person fontSize="small" />
                </Avatar>
              )}
            </Box>
          ))}

          {loading && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                mb: 2,
              }}
            >
              <Avatar
                sx={{
                  bgcolor: 'secondary.main',
                  mr: 1,
                  width: 32,
                  height: 32,
                }}
              >
                <SmartToy fontSize="small" />
              </Avatar>

              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  bgcolor: 'background.paper',
                  borderRadius: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    Alex está escribiendo...
                  </Typography>
                </Box>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Container>
      </Box>

      {/* Input Area */}
      <Paper
        elevation={8}
        sx={{
          p: 2,
          borderRadius: 0,
        }}
      >
        <Container maxWidth="md">
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje..."
              disabled={loading}
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />

            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={!input.trim() || loading}
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '&.Mui-disabled': {
                  bgcolor: 'action.disabledBackground',
                },
              }}
            >
              <Send />
            </IconButton>
          </Box>

          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: 'block', mt: 1, textAlign: 'center' }}
          >
            Este chat es privado y confidencial. No se almacena ninguna conversación.
          </Typography>
        </Container>
      </Paper>
    </Box>
  );
}
