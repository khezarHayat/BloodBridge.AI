/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        crimson: {
          DEFAULT: '#C8102E',
          50: '#FDF2F4',
          100: '#FBE6E9',
          200: '#F5C2C9',
          300: '#EF9DAA',
          400: '#E4556C',
          500: '#C8102E',
          600: '#B40E29',
          700: '#960C22',
          800: '#780A1C',
          900: '#5A0715',
        },
        navy: {
          DEFAULT: '#14213D',
          50: '#F0F3F8',
          100: '#E1E7F1',
          200: '#B8C6DE',
          300: '#8FA5CA',
          400: '#3D62A2',
          500: '#14213D',
          600: '#121E37',
          700: '#0E172B',
          800: '#0B1221',
          900: '#070C16',
        },
        charcoal: {
          DEFAULT: '#252A34',
          50: '#F7F8F9',
          100: '#EFF0F2',
          200: '#D7D9DE',
          300: '#BFC2CA',
          400: '#8F94A2',
          500: '#252A34',
          600: '#21262F',
          700: '#1A1E25',
          800: '#14171D',
          900: '#0E1014',
        },
        surface: '#F5F7FA',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
        'card': '0 4px 6px -1px rgba(20, 33, 61, 0.05), 0 2px 4px -2px rgba(20, 33, 61, 0.05)',
        'elevated': '0 10px 15px -3px rgba(20, 33, 61, 0.08), 0 4px 6px -4px rgba(20, 33, 61, 0.04)',
      },
    },
  },
  plugins: [],
}
