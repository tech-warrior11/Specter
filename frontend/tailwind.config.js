/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#090d16",
          card: "#0f172a",
          cardHover: "#1e293b",
          border: "#1e293b",
          cyan: "#06b6d4",
          blue: "#3b82f6",
          purple: "#8b5cf6",
          red: "#ef4444",
          amber: "#f59e0b",
          green: "#10b981",
          muted: "#64748b"
        }
      }
    },
  },
  plugins: [],
}
