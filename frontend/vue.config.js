const path = require('path');

module.exports = {
  pages: {
    index: {
      entry: './main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: 'Quiz Master v2'
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './')
      }
    }
  },
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Flask backend URL
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' }
      }
    }
  }
};
