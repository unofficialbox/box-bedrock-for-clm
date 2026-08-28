import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import salesforce from "@salesforce/vite-plugin-ui-bundle";

export default defineConfig(({ command, mode }) => ({
  base: "./",
  plugins: [
    react(),
    ...(command === "build" && mode !== "standalone" ? [salesforce()] : []),
  ],
  // Some box-ui-elements dependencies (draft-js and friends) reference the Node `global`.
  // Browsers do not define it, and without this the app throws before React mounts.
  define: {
    global: "globalThis",
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
}));
