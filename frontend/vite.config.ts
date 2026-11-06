import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development the browser talks to Vite on :5173, which forwards API calls to the backend on :8000.
// Same origin for the browser means cookies just work (book Chapter 11).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/v1": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
