module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0B0F19',
          800: '#111827',
          700: '#1E293B',
          600: '#334155',
          500: '#475569',
        },
        surface: {
          DEFAULT: 'rgba(255, 255, 255, 0.04)',
          hover: 'rgba(255, 255, 255, 0.08)',
          border: 'rgba(255, 255, 255, 0.08)',
          'border-hover': 'rgba(255, 255, 255, 0.15)',
        },
        accent: {
          DEFAULT: '#6366F1',
          light: '#818CF8',
          lighter: '#A5B4FC',
          dark: '#4F46E5',
          glow: 'rgba(99, 102, 241, 0.15)',
          'glow-strong': 'rgba(99, 102, 241, 0.3)',
        },
        txt: {
          primary: '#F8FAFC',
          secondary: '#94A3B8',
          muted: '#64748B',
        },
        status: {
          success: '#34D399',
          'success-bg': 'rgba(52, 211, 153, 0.1)',
          danger: '#FB7185',
          'danger-bg': 'rgba(251, 113, 133, 0.1)',
          warning: '#FBBF24',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.3)',
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.2)',
        'glow': '0 0 40px rgba(99, 102, 241, 0.15)',
        'glow-lg': '0 0 60px rgba(99, 102, 241, 0.25)',
      },
      animation: {
        'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-down': 'slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in': 'fadeIn 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gauge-fill': 'gaugeFill 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'count-up': 'fadeIn 0.8s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        gaugeFill: {
          '0%': { strokeDashoffset: '283' },
          '100%': { strokeDashoffset: 'var(--gauge-target)' },
        },
      },
    },
  },
  plugins: [],
}
