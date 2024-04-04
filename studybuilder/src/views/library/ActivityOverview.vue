<template>
<div v-if="activityOverview" class="px-4">
  <div class="d-flex page-title">
    {{ activityOverview.activity.name }}
    <help-button-with-panels :help-text="$t('_help.ActivityOverview.general')" :items="helpItems"/>
  </div>
  <activity-overview
    v-if="activityOverview"
    source="activities"
    :item-uid="$route.params.id"
    :item-overview="activityOverview"
    :yaml-version="activityYAML"
    :cosmos-version="activityCOSMoS"
    @refresh="fetchOverview"
    @closePage="closePage"
    />
</div>
</template>

<script>
import ActivityOverview from '@/components/library/ActivityOverview'
import activities from '@/api/activities'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'
import { mapActions } from 'vuex'

export default {
  components: {
    ActivityOverview,
    HelpButtonWithPanels
  },
  data () {
    return {
      activityOverview: null,
      activityYAML: null,
      activityCOSMoS: null,
      helpItems: [
        'ActivityOverview.cosmos_yaml',
        'ActivityOverview.activity_groups',
        'ActivityOverview.activity_subgroups',
        'ActivityOverview.adam_code',
        'ActivityOverview.topic_code',
        'ActivityOverview.class',
        'ActivityOverview.instances',
        'ActivityOverview.is_data_collected',
        'ActivityOverview.activity_groupings'
      ]
    }
  },
  created () {
    this.fetchOverview()
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    fetchOverview () {
      activities.getObjectOverview('activities', this.$route.params.id).then(resp => {
        this.activityOverview = resp.data
        this.addBreadcrumbsLevel({
          text: this.activityOverview.activity.name,
          to: { name: 'ActivityOverview', params: this.$route.params },
          index: 4
        })
      })
      activities.getObjectOverview('activities', this.$route.params.id, 'yaml').then(resp => {
        this.activityYAML = resp.data
      })
      activities.getCOSMoSOverview('activities', this.$route.params.id).then(resp => {
        this.activityCOSMoS = resp.data
      })
    },
    closePage () {
      this.$router.go(-1)
    }
  }
}
</script>
