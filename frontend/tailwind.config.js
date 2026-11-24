/** @type {import('tailwindcss').Config} */

// The slate palette is backed by CSS custom properties (see main.css) so the
// whole app can switch between the dark and light palettes with one attribute.
const slate = (shade) => `rgb(var(--c-slate-${shade}) / <alpha-value>)`;

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
      },
      colors: {
        slate: {
          50: slate(50),
          100: slate(100),
          200: slate(200),
          300: slate(300),
          400: slate(400),
          500: slate(500),
          600: slate(600),
          700: slate(700),
          800: slate(800),
          900: slate(900),
          950: slate(950),
        },
      },
    },
  },
  plugins: [],
};
