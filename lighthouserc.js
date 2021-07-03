module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:8000/'],
      startServerCommand: 'docker-compose -f docker-compose.yml -f docker-compose.prod.yml up',
      startServerReadyTimeout: 60000,
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
