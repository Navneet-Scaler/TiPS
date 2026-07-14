/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        base: {
          bg: "#0b0d12",
          panel: "#12151c",
          panel2: "#171b24",
          border: "#232834",
          text: "#e7e9ee",
          muted: "#8b93a3",
        },
        accent: {
          DEFAULT: "#5b8cff",
          soft: "#2a3a63",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
