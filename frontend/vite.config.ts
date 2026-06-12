import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import react from "@vitejs/plugin-react-swc"
import { defineConfig, loadEnv } from "vite"

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")
  const caddyDev = env.VITE_CADDY_DEV === "true"
  const caddyHost = env.VITE_CADDY_HOST ?? "dashboard.localhost.tiangolo.com"

  return {
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    ...(caddyDev
      ? {
          hmr: {
            host: caddyHost,
            protocol: "wss",
            clientPort: 443,
          },
        }
      : {}),
  },
  plugins: [
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
    }),
    react(),
    tailwindcss(),
  ],
  }
})
