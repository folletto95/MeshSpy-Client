// tailwind.config.js
import { defineConfig } from "vite";

export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        meshtastic: "#00c853", // verde ufficiale
      },
    },
  },
  plugins: [],
};
