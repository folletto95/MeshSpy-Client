// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class", // <=== Attivazione dark mode
  theme: {
    extend: {
      colors: {
        meshtastic: "#00c853",
      },
    },
  },
  plugins: [],
};