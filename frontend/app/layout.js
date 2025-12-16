import ThemeRegistry from './ThemeRegistry';

export const metadata = {
  title: "Escudo Escolar - Sistema de Detección de Bullying",
  description: "Plataforma de detección temprana de bullying con inteligencia artificial",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <ThemeRegistry>
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}
