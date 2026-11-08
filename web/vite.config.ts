import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const API = "http://127.0.0.1:8000";
const API_PATHS = ["/city", "/neighborhoods", "/hazard", "/overlays", "/validation", "/brief", "/limits"];

export default defineConfig({
  plugins: [react()],
  server: { proxy: Object.fromEntries(API_PATHS.map((path) => [path, API])) },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/testSetup.ts"],
    css: { include: [/tokens\.css/] },
  },
});
