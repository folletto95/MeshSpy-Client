/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        meshtastic: "#5b21b6", // viola custom per branding
      },
    },
  },
  plugins: [],
};
