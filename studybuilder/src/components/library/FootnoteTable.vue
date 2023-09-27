<template>
<div>
  <instance-table
    fetch-instances-action-name="footnotes/fetchFilteredFootnotes"
    type="footnote"
    :instances="footnotes"
    base-url="/footnotes"
    export-object-label="Footnotes"
    column-data-resource="footnotes"
    />
</div>
</template>

<script>
import InstanceTable from './InstanceTable'
import { mapGetters } from 'vuex'

export default {
  components: {
    InstanceTable
  },
  computed: {
    ...mapGetters({
      footnotes: 'footnotes/footnotes'
    })
  }
}
</script>
