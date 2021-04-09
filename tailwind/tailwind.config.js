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
  variants: {
    extend: {
      cursor: ['responsive', 'disabled'],
      backgroundColor: ['responsive', 'hover', 'focus', 'disabled'],
      fontWeight: ['responsive', 'hover', 'focus', 'disabled'],
      textColor: ['responsive', 'hover', 'focus', 'disabled'],
      transitionProperty: ['responsive', 'motion-safe', 'motion-reduce'],
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
