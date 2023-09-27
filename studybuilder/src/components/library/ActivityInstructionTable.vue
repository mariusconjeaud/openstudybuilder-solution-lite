<template>
<div>
  <instance-table
    fetch-instances-action-name="activityInstructions/fetchFilteredActivityInstructions"
    type="activity_instruction"
    :instances="activityInstructions"
    base-url="/activity-instructions"
    export-object-label="ActivityInstructions"
    column-data-resource="activityInstructions"
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
      activityInstructions: 'activityInstructions/activityInstructions',
      total: 'activityInstructions/total'
    })
  }
}
</script>
