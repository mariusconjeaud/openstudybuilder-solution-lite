import Vue from 'vue'

// Methods and constants defined in this file are globally accessible

Vue.mixin({
  methods: {
    getHtmlLineBreaks (value) {
      return (value ? value.replaceAll('\n', '<br />') : '')
    },
    getTermOrderInCodelist (term, codelistUid) {
      let order = ''
      if (term.codelists) {
        term.codelists.forEach(x => {
          if (x.codelist_uid === codelistUid) {
            order = x.order
          }
        })
      }
      return order
    }
  },
  data: function () {
    return {
      globalHistoryDialogMaxWidth: '1600px',
      globalHistoryDialogFullscreen: true
    }
  }
})
