module.exports = {
  mode: 'jit',
  purge: {
    content: [
      '../templates/**/*.html',
      '../**/templates/**/*.html',
    ],
    options: {
      fontFace: true,
      keyframes: true,
      // variables: true,
    },
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
