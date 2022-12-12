export const studyMetadataFormMixin = {
  methods: {
    getTermPayload (name) {
      if (this.form[name]) {
        return {
          term_uid: this.form[name].term_uid,
          name: this.form[name].sponsor_preferred_name || this.form[name].name
        }
      }
      return null
    },
    getTermsPayload (name) {
      const result = []
      if (!this.form[name]) {
        return null
      }
      this.form[name].forEach(term => {
        result.push({
          term_uid: term.term_uid,
          name: term.sponsor_preferred_name || term.name
        })
      })
      return result
    }
  }
}
