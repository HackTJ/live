module.exports = {
  mode: 'jit',
  content: [
    '../templates/**/*.html',
    '../**/templates/**/*.html',
  ],
  darkMode: 'media', // or 'class'
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
