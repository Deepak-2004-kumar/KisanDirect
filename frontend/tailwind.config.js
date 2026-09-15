/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        leaf: {
          50: '#f1f9ee', 100: '#dcf0d4', 300: '#a3d98c', 500: '#5da838',
          600: '#4a8a2c', 700: '#3a6d22', 900: '#22400f',
        },
        wheat: { 100: '#fdf6e3', 400: '#e8c468', 600: '#c9982e' },
      },
      fontFamily: { sans: ['Inter', 'Noto Sans', 'sans-serif'] },
    },
  },
  plugins: [],
}
