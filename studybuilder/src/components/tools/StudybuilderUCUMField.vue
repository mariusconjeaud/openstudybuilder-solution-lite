<template>
<div>
  <v-autocomplete
    :label="$t('UCUMUnitField.label')"
    :value="value"
    :items="ucumUnits"
    item-value="term_uid"
    item-text="name"
    return-object
    dense
    clearable
    v-bind="$attrs"
    v-on="$listeners"
    @change="update"
    />
</div>
</template>

<script>
import dictionaries from '@/api/dictionaries'

export default {
  props: ['value'],
  data () {
    return {
      ucumUnits: []
    }
  },
  mounted () {
    dictionaries.getCodelists('UCUM').then(resp => {
      const params = {
        codelist_uid: resp.data.items[0].codelist_uid
      }
      dictionaries.getTerms(params).then(resp => {
        this.ucumUnits = resp.data.items
      })
    })
  },
  methods: {
    update (value) {
      this.$emit('input', value)
    }
  }
}
</script>
