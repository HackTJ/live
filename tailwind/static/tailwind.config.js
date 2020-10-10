module.exports = {
  purge: {
    enabled: true,
    content: [
      '../../templates/**/*.html',
      '../../**/templates/**/*.html'
    ]
  },
  theme: {
    extend: {}
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
  future: {
    removeDeprecatedGapUtilities: true,
    purgeLayersByDefault: true,
  },
  experimental: {
    uniformColorPalette: true,
    extendedSpacingScale: true,
    defaultLineHeights: true,
    extendedFontSizeScale: true,
  },
}
