// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class", // ⬅️ aggiunto
  theme: {
    extend: {
      colors: {
        meshtastic: "#00c853",
      },
    },
  },
  plugins: [],
};

