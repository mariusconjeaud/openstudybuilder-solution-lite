import Vue from 'vue'

// Methods and constants defined in this file are globally accessible

Vue.mixin({
  methods: {
    getHtmlLineBreaks (value) {
      return (value ? value.replaceAll('\n', '<br />') : '')
    }
  },
  data: function () {
    return {
      globalHistoryDialogMaxWidth: '1600px',
      globalHistoryDialogFullscreen: true
    }
  }
})
