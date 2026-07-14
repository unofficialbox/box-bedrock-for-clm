import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import salesforce from "@salesforce/vite-plugin-ui-bundle";

export default defineConfig(({ command, mode }) => ({
  base: "./",
  plugins: [
    react(),
    ...(command === "build" && mode !== "standalone" ? [salesforce()] : []),
  ],
  build: {
    outDir: "dist",
    sourcemap: false,
  },
}));
