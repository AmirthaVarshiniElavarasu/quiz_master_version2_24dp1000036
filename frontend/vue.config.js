// frontend/vue.config.js
const path = require('path');

module.exports = {
  pages: {
    index: {
      entry: './main.js',
      template: 'public/index.html',
      filename: 'index.html'
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './')
      }
    }
  }
};
