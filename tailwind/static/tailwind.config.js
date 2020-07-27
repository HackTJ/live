module.exports = {
  purge: [],
  theme: {
    extend: {},
  },
  variants: {
    cursor: ['responsive', 'disabled'],
    backgroundColor: ['responsive', 'hover', 'focus', 'disabled'],
    fontWeight: ['responsive', 'hover', 'focus', 'disabled'],
    textColor: ['responsive', 'hover', 'focus', 'disabled']
  },
  plugins: [
    require('@tailwindcss/custom-forms')
  ],
}
