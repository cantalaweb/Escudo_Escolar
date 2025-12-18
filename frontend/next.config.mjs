/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    root: process.cwd(),
  },
  // Habilitar modo standalone para Docker (optimizado para producción)
  output: 'standalone',
};

export default nextConfig;
