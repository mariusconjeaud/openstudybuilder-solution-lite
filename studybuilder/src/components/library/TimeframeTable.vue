<template>
<div>
  <instance-table
    fetch-instances-action-name="timeframes/fetchFilteredTimeframes"
    type="timeframe"
    :instances="timeframes"
    base-url="/timeframes"
    export-object-label="Timeframes"
    column-data-resource="timeframes"
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
      timeframes: 'timeframes/timeframes'
    })
  }
}
</script>
