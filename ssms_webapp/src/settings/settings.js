console.log(`ENV: ${process.env.NODE_ENV}`)

if (process.env.NODE_ENV === 'development') {
  module.exports = require('./settings.dev');
} else {
  module.exports = require('./settings.prod');
}
