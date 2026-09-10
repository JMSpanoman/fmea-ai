/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: 'var(--sr-color-brand)',
          hover: 'var(--sr-color-brand-hover)',
          muted: 'var(--sr-color-brand-muted)',
          foreground: 'var(--sr-color-brand-foreground)',
        },
        navy: 'var(--sr-color-navy)',
        ink: 'var(--sr-color-ink)',
        muted: 'var(--sr-color-muted)',
        subtle: 'var(--sr-color-subtle)',
        canvas: 'var(--sr-color-canvas)',
        healthy: {
          DEFAULT: 'var(--sr-color-healthy)',
          muted: 'var(--sr-color-healthy-muted)',
        },
        attention: {
          DEFAULT: 'var(--sr-color-attention)',
          muted: 'var(--sr-color-attention-muted)',
        },
        info: {
          DEFAULT: 'var(--sr-color-info)',
          muted: 'var(--sr-color-info-muted)',
        },
        draft: {
          DEFAULT: 'var(--sr-color-draft)',
          muted: 'var(--sr-color-draft-muted)',
        },
        background: {
          main: 'var(--sr-color-canvas)',
          secondary: 'var(--sr-color-surface)',
        },
        surface: {
          primary: 'var(--sr-color-surface)',
          secondary: 'var(--sr-color-neutral-muted)',
        },
        primary: {
          DEFAULT: 'var(--sr-color-brand)',
          hover: 'var(--sr-color-brand-hover)',
        },
        success: 'var(--sr-color-healthy)',
        danger: 'var(--sr-color-danger)',
        text: {
          primary: 'var(--sr-color-ink)',
          secondary: 'var(--sr-color-muted)',
        },
        border: 'var(--sr-color-border)',
      },
      fontFamily: {
        sans: ['var(--sr-font-sans)', 'Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        h1: ['1.75rem', { lineHeight: '1.2', fontWeight: '700' }],
        h2: ['1.375rem', { lineHeight: '1.3', fontWeight: '600' }],
        h3: ['1.125rem', { lineHeight: '1.4', fontWeight: '600' }],
        body: ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
        header: 'var(--sr-header-height)',
        sidebar: 'var(--sr-sidebar-width)',
      },
      minHeight: {
        control: 'var(--sr-control-height-md)',
        'control-lg': 'var(--sr-control-height-lg)',
      },
      height: {
        control: 'var(--sr-control-height-md)',
        'control-lg': 'var(--sr-control-height-lg)',
        header: 'var(--sr-header-height)',
      },
      width: {
        sidebar: 'var(--sr-sidebar-width)',
      },
      borderRadius: {
        card: 'var(--sr-radius-lg)',
        control: 'var(--sr-radius-md)',
        button: 'var(--sr-radius-md)',
      },
      boxShadow: {
        card: 'var(--sr-shadow-card)',
        header: 'var(--sr-shadow-header)',
        focus: 'var(--sr-shadow-focus)',
        elevated: '0 8px 24px rgba(21, 32, 51, 0.08)',
        glow: '0 0 0 3px rgba(15, 107, 110, 0.18)',
      },
      backdropBlur: {
        glass: '10px',
      },
    },
  },
  plugins: [],
};
