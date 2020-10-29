module.exports = {
  purge: [
    '../../templates/**/*.html',
    '../../**/templates/**/*.html'
  ],
  darkMode: false,
  theme: {
    extend: {},
  },
  variants: {
    extend: {
      cursor: ['responsive', 'disabled'],
      backgroundColor: ['responsive', 'hover', 'focus', 'disabled'],
      fontWeight: ['responsive', 'hover', 'focus', 'disabled'],
      textColor: ['responsive', 'hover', 'focus', 'disabled']
    },
  },
  plugins: [
    // require('@tailwindcss/custom-forms'),
  ],
}
