/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5', // Indigo/Deep Purple
        'primary-light': '#6366F1', // Lighter Indigo
        'dark-bg': '#111827', // Dark Gray/Near Black
        'dark-card': '#1F2937', // Medium Dark Gray
        'dark-border': '#374151', // Lighter Dark Gray
        'light-bg': '#F9FAFB', // Very Light Gray/Off-White
        'light-text': '#111827', // Dark Gray/Near Black
        'light-text-secondary': '#6B7280', // Medium Gray
        'dark-text': '#FFFFFF', // White
        'dark-text-secondary': '#D1D5DB', // Light Gray
        success: '#10B981', // Green
        warning: '#F59E0B', // Amber/Yellow
        error: '#EF4444', // Red
        info: '#3B82F6', // Blue
        accent: '#EC4899', // Pink
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Primary and Secondary font
      },
    },
  },
  plugins: [],
}
