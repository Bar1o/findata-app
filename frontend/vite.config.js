import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["@gravity-ui/uikit"],
  },
  preview: {
    port: 3001,
  },
  server: {
    port: 3001,
    proxy: {
      // Proxy API requests to the backend server
      "/api": {
        target: "http://localhost:3300",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
