module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:1379/'],
      startServerCommand: 'docker-compose -f docker-compose.yml -f docker-compose.prod.yml up',
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
