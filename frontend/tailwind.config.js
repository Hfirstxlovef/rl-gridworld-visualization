/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 宇宙主题配色
        'space-dark': '#0a0a1a',
        'space-blue': '#1a1a3e',
        'nebula-blue': '#4a90d9',
        'nebula-purple': '#8b5cf6',
        'star-gold': '#fbbf24',
        'tech-green': '#10b981',
        'aurora-purple': '#a855f7',
        'warning-orange': '#f97316',
        'danger-red': '#ef4444',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #4a90d9, 0 0 10px #4a90d9' },
          '100%': { boxShadow: '0 0 20px #4a90d9, 0 0 30px #4a90d9' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
  // 与 Ant Design 兼容
  corePlugins: {
    preflight: false,
  },
}
