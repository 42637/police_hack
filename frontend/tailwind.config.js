/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#030712",        // Deep FBI Dark Navy
          card: "rgba(17, 24, 39, 0.7)", // Glassmorphic background
          cardBorder: "rgba(31, 41, 55, 0.5)",
          neonGreen: "#10b981", // Active / Safe Green
          neonCyan: "#06b6d4",  // Vehicle Intelligence Cyan
          neonPurple: "#a855f7", // System Log Purple
          neonRed: "#ef4444",   // Critical Alarm Red
          neonYellow: "#eab308" // Warn Yellow
        }
      },
      backgroundImage: {
        'cyber-gradient': 'radial-gradient(circle at 50% 50%, #0d1527 0%, #030712 100%)',
        'aurora-cyan': 'radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.15) 0%, transparent 40%)',
        'aurora-purple': 'radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.15) 0%, transparent 45%)'
      },
      boxShadow: {
        'glow-green': '0 0 15px rgba(16, 185, 129, 0.45)',
        'glow-cyan': '0 0 15px rgba(6, 182, 212, 0.45)',
        'glow-red': '0 0 15px rgba(239, 68, 68, 0.45)',
        'glow-purple': '0 0 15px rgba(168, 85, 247, 0.45)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scan 8s linear infinite',
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' }
        }
      }
    },
  },
  plugins: [],
}
