define([], function() {
  'use strict';

  require.config({
    paths: {
      'jquery': '/bower_components/jquery/dist/jquery.min',
      'angular': '/bower_components/angular/angular'
    },
    shim: {
      'angular': {
        exports: 'angular'
      }
     }
  });
});