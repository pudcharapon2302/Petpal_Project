// theme/static_src/src/tailwind.config.js

module.exports = {
  content: [
      // 1. สแกนไฟล์ .html ของแอป 'theme' เอง
      '../templates/**/*.html', 

      // 2. (สำคัญ) สแกนไฟล์ .html ของ 'myapp'
      '../../myapp/templates/myapp/**/*.html',
      '../../myapp/templates/myapp/partials/**/*.html',
  ],
  theme: {
    extend: {
      keyframes: {
        shimmer: {
          '100%': { backgroundPosition: '-200% center' },
        }
      },
      animation: {
        shimmer: 'shimmer 1.5s linear infinite',
      }
    },
  },
  plugins: [],
}
