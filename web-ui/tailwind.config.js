/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                thunder: {
                    900: '#0f172a',
                    800: '#1e293b',
                    700: '#334155',
                    600: '#475569',
                    500: '#64748b',
                    400: '#94a3b8',
                    accent: '#3b82f6', // Blue accent
                    danger: '#ef4444',
                    success: '#22c55e',
                    warning: '#eab308'
                }
            }
        },
    },
    plugins: [],
}
