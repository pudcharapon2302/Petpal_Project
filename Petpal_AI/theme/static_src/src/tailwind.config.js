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
    extend: {},
  },
  plugins: [],
}