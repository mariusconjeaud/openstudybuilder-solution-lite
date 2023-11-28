<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('Sidebar.library.activities') }}
    <help-button-with-panels :help-text="$t('_help.ActivitiesTable.general')" :items="helpItems"/>
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
        source="activity-groups"
        />
    </v-tab-item>
    <v-tab-item id="activity-subgroups">
      <activities-table
        source="activity-sub-groups"
        />
    </v-tab-item>
    <v-tab-item id="activities-by-grouping">
      <activities-table
        source="activities-by-grouping"
        />
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
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'
import { mapActions } from 'vuex'

export default {
  components: {
    ActivitiesTable,
    HelpButtonWithPanels
  },
  data () {
    return {
      tab: null,
      tabs: [
        { tab: '#activities', name: this.$t('ActivityTable.activities') },
        { tab: '#activity-groups', name: this.$t('ActivityTable.activity_groups') },
        { tab: '#activity-subgroups', name: this.$t('ActivityTable.activity_subgroups') },
        { tab: '#activities-by-grouping', name: this.$t('ActivityTable.activities_overview') },
        { tab: '#activity-instances', name: this.$t('ActivityTable.instances') },
        { tab: '#requested-activities', name: this.$t('ActivityTable.requested') }
      ],
      helpItems: [
        'ActivityTable.activities',
        'ActivityTable.activity_groups',
        'ActivityTable.activity_subgroups',
        'ActivityTable.activities_overview',
        'ActivityTable.instances',
        'ActivityTable.requested',
        'ActivityTable.activity_name',
        'ActivityTable.sentence_case_name',
        'ActivityTable.abbreviation',
        'ActivityTable.definition',
        'ActivityTable.nci_concept_id',
        'ActivityTable.topic_code',
        'ActivityTable.adam_code',
        'ActivityTable.activity_group',
        'ActivityTable.activity_subgroup',
        'ActivityTable.is_data_collected',
        'ActivityTable.activity',
        'ActivityTable.instance',
        'ActivityTable.is_required_for_activity',
        'ActivityTable.is_default_selected_for_activity',
        'ActivityTable.is_data_sharing',
        'ActivityTable.is_legacy_usage',
        'ActivityTable.rationale_for_request'
      ]
    }
  },
  created () {
    this.tab = this.$route.params.tab
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  watch: {
    tab (newValue) {
      const tab = newValue || this.tabs[0].tab
      this.$router.push({
        name: 'Activities',
        params: { tab }
      })
      const tabName = this.tabs.find(el => el.tab.substring(1) === tab).name
      this.addBreadcrumbsLevel({
        text: tabName,
        to: { name: 'Activities', params: { tab } },
        index: 3,
        replace: true
      })
    }
  }
}
</script>
