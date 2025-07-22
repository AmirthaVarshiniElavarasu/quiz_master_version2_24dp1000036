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
