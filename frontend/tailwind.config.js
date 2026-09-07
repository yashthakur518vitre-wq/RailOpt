/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        ink: { DEFAULT: '#0F1720', panel: '#16202B', track: '#2A3A48' },
        signal: {
          green: '#2FA84F',
          amber: '#E8A33D',
          red: '#D64545',
        },
        steel: {
          DEFAULT: '#3E7CB1',
          light: '#5C93C4',
          dark: '#2C5A80',
        },
        success: '#2FA84F',
        warning: '#E8A33D',
        danger: '#D64545',
      },
      borderRadius: {
        panel: '10px',
      },
    },
  },
  plugins: [],
}
