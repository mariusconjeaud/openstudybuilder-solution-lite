<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.library.activities') }}
    <help-button :help-text="$t('_help.ActivitiesTable.general')" />
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">{{ tab.name }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="activities">
      <activities-table
        source="activities"/>
    </v-tab-item>
    <v-tab-item id="activity-groups">
      <activities-table
        source="activity-groups"/>
    </v-tab-item>
    <v-tab-item id="activity-instances">
      <activities-table
        source="activity-instances"/>
    </v-tab-item>
    <v-tab-item id="requested-activities">
      <activities-table
        source="activities" requested/>
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import ActivitiesTable from '@/components/library/ActivitiesTable'
import HelpButton from '@/components/tools/HelpButton'
import { mapActions } from 'vuex'

export default {
  components: {
    ActivitiesTable,
    HelpButton
  },
  data () {
    return {
      tab: 0,
      tabs: [
        { tab: '#activities', name: this.$t('ActivityTable.activities') },
        { tab: '#activity-groups', name: this.$t('ActivityTable.activities_overview') },
        { tab: '#activity-instances', name: this.$t('ActivityTable.instances') },
        { tab: '#requested-activities', name: this.$t('ActivityTable.requested') }
      ]
    }
  },
  mounted () {
    this.tab = this.$route.params.tab
    const tabName = this.tab ? this.tabs.find(el => el.tab.substring(1) === this.tab).name : this.tabs[0].name
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'StudyProperties', params: { tab: tabName } },
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  watch: {
    tab (newValue) {
      this.$router.push({
        name: 'Activities',
        params: { tab: newValue }
      })
      const tabName = newValue ? this.tabs.find(el => el.tab.substring(1) === newValue).name : this.tabs[0].name
      this.addBreadcrumbsLevel({
        text: tabName,
        index: 3,
        replace: true
      })
    }
  }
}
</script>
