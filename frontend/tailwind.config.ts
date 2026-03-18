/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Design system colors
        background: {
          main: '#050816',
          secondary: '#0B1020',
        },
        surface: {
          primary: '#0E172A',
          secondary: '#111827',
        },
        primary: {
          DEFAULT: '#C4B5FD',   // light purple (readable with dark text)
          hover: '#A78BFA',
        },
        success: '#22C55E',
        danger: '#EF4444',
        text: {
          primary: '#000000',
          secondary: '#000000',
        },
        border: 'rgba(148, 163, 184, 0.35)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'h1': ['28px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['22px', { lineHeight: '1.3', fontWeight: '600' }],
        'h3': ['18px', { lineHeight: '1.4', fontWeight: '500' }],
        'body': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      borderRadius: {
        'card': '0.75rem',
        'button': '9999px',
      },
      boxShadow: {
        'elevated': '0 10px 30px rgba(15, 23, 42, 0.8)',
        'glow': '0 0 20px rgba(196, 181, 253, 0.4)',
      },
      backdropBlur: {
        'glass': '10px',
      },
    },
  },
  plugins: [],
}
