import { defineConfig } from 'vite';
const domainName = import.meta.env.VITE_DOMAIN_NAME || 'localhost';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    allowedHosts: [domainName]
  }
});
