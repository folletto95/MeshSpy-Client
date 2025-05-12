/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        meshtastic: "#27ae60", // Verde acceso stile Meshtastic
      },
    },
  },
  plugins: [],
};
