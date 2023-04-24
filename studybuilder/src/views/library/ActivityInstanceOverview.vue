<template>
<div v-if="activityInstance" class="px-4">
  <div class="d-flex page-title">
    {{ activityInstance.activity_instance.name }}
  </div>
  <activity-instance-overview
    v-if="activityInstance"
    :activity-instance="activityInstance"
    :yaml-version="activityInstanceYAML"
    />
</div>
</template>

<script>
import ActivityInstanceOverview from '@/components/library/ActivityInstanceOverview'
import activities from '@/api/activities'
import { mapActions } from 'vuex'

export default {
  components: {
    ActivityInstanceOverview
  },
  data () {
    return {
      activityInstance: null,
      activityInstanceYAML: null
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  created () {
    activities.getObjectOverview('activity-instances', this.$route.params.id).then(resp => {
      this.activityInstance = resp.data
      this.addBreadcrumbsLevel({
        text: this.activityInstance.activity_instance.name,
        to: { name: 'ActivityInstanceOverview', params: this.$route.params },
        index: 4
      })
    })
    activities.getObjectOverview('activity-instances', this.$route.params.id, 'yaml').then(resp => {
      this.activityInstanceYAML = resp.data
    })
  }
}
</script>
