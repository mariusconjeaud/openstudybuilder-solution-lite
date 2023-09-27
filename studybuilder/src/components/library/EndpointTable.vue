<template>
<div>
  <instance-table
    fetch-instances-action-name="endpoints/fetchFilteredEndpoints"
    type="endpoint"
    :instances="endpoints"
    base-url="/endpoints"
    export-object-label="Endpoints"
    column-data-resource="endpoints"
    :server-items-length="total"
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
      endpoints: 'endpoints/endpoints',
      total: 'endpoints/total'
    })
  }
}
</script>
