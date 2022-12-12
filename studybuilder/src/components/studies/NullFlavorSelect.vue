<template>
<div>
  <v-select
    :label="$t('NullFlavorSelect.label')"
    :value="value"
    :items="nullValues"
    item-text="sponsor_preferred_name"
    item-value="term_uid"
    return-object
    :error-messages="errors"
    @input="update"
    dense
    clearable
    data-cy="select-null-value"
    v-bind="$attrs"
    />
</div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  props: ['value', 'errors'],
  computed: {
    ...mapGetters({
      nullValues: 'studiesGeneral/nullValues'
    })
  },
  methods: {
    update (val) {
      const newValue = {
        term_uid: val.term_uid,
        name: val.sponsor_preferred_name || val.name
      }
      this.$emit('input', newValue)
    }
  }
}
</script>
