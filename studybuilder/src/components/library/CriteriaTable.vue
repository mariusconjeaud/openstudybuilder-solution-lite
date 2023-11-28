<template>
<div>
  <instance-table
    fetch-instances-action-name="criteria/fetchFilteredCriteria"
    :fetch-instances-extra-filters="extraFilters"
    type="criteria"
    :instances="criteria"
    base-url="/criteria"
    export-object-label="Criteria"
    column-data-resource="criteria"
    :server-items-length="total"
    :instance-type="criteriaType.term_uid"
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
  props: {
    criteriaType: Object
  },
  computed: {
    ...mapGetters({
      criteria: 'criteria/criteria',
      total: 'criteria/total'
    }),
    extraFilters () {
      return {
        'criteria_template.type.term_uid': { v: [this.criteriaType.term_uid], op: 'eq' }
      }
    }
  }
}
</script>
