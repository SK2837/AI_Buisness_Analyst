/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                plex: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui'],
                'plex-serif': ['"IBM Plex Serif"', 'ui-serif', 'Georgia'],
            },
        },
    },
    plugins: [],
}
