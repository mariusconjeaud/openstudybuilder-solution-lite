<template>
<div v-if="activity" class="px-4">
  <div class="d-flex page-title">
    {{ activity.activity.name }}
    <help-button :help-text="$t('_help.ActivityOverview.general')" />
  </div>
  <activity-overview
    v-if="activity"
    :activity="activity"
    :yaml-version="activityYAML"
    />
</div>
</template>

<script>
import ActivityOverview from '@/components/library/ActivityOverview'
import activities from '@/api/activities'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'

export default {
  components: {
    ActivityOverview,
    HelpButton
  },
  data () {
    return {
      activity: null,
      activityYAML: null
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  created () {
    activities.getObjectOverview('activities', this.$route.params.id).then(resp => {
      this.activity = resp.data
      this.addBreadcrumbsLevel({
        text: this.activity.activity.name,
        to: { name: 'ActivityOverview', params: this.$route.params },
        index: 4
      })
    })
    activities.getObjectOverview('activities', this.$route.params.id, 'yaml').then(resp => {
      this.activityYAML = resp.data
    })
  }
}
</script>
