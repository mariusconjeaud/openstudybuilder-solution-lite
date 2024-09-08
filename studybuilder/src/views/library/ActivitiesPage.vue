<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('Sidebar.library.activities') }}
      <HelpButtonWithPanels
        :help-text="$t('_help.ActivitiesTable.general')"
        :items="helpItems"
      />
    </div>
    <v-tabs v-model="tab" bg-color="white">
      <v-tab v-for="item of tabs" :key="item.tab" :value="item.tab">
        {{ item.name }}
      </v-tab>
    </v-tabs>
    <v-window v-model="tab">
      <v-window-item value="activities">
        <ActivitiesTable
          :key="`activities-${tabKeys['activities']}`"
          source="activities"
        />
      </v-window-item>
      <v-window-item value="activity-groups">
        <ActivitiesTable
          :key="`activities-${tabKeys['activity-groups']}`"
          source="activity-groups"
        />
      </v-window-item>
      <v-window-item value="activity-subgroups">
        <ActivitiesTable
          :key="`activities-${tabKeys['activity-subgroups']}`"
          source="activity-sub-groups"
        />
      </v-window-item>
      <v-window-item value="activities-by-grouping">
        <ActivitiesTable
          :key="`activities-${tabKeys['activities-by-grouping']}`"
          source="activities-by-grouping"
        />
      </v-window-item>
      <v-window-item value="activity-instances">
        <ActivitiesTable
          :key="`activities-${tabKeys['activity-instances']}`"
          source="activity-instances"
        />
      </v-window-item>
      <v-window-item value="requested-activities">
        <ActivitiesTable
          :key="`activities-${tabKeys['requested-activities']}`"
          source="activities"
          requested
        />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import ActivitiesTable from '@/components/library/ActivitiesTable.vue'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels.vue'
import { useAppStore } from '@/stores/app'
import { useRoute, useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTabKeys } from '@/composables/tabKeys'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const { t } = useI18n()
const { tabKeys, updateTabKey } = useTabKeys()

const tab = ref(null)
const tabs = [
  { tab: 'activities', name: t('ActivityTable.activities') },
  {
    tab: 'activity-groups',
    name: t('ActivityTable.activity_groups'),
  },
  {
    tab: 'activity-subgroups',
    name: t('ActivityTable.activity_subgroups'),
  },
  {
    tab: 'activities-by-grouping',
    name: t('ActivityTable.activities_overview'),
  },
  { tab: 'activity-instances', name: t('ActivityTable.instances') },
  {
    tab: 'requested-activities',
    name: t('ActivityTable.requested'),
  },
]
const helpItems = [
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
  'ActivityTable.rationale_for_request',
]

watch(tab, (newValue) => {
  const activeTab = newValue || tabs[0].tab
  router.push({
    name: 'Activities',
    params: { tab: newValue },
  })
  const tabName = tabs.find((el) => el.tab === activeTab).name
  appStore.addBreadcrumbsLevel(
    tabName,
    { name: 'Activities', params: { tab: tabName } },
    3,
    true
  )
  updateTabKey(newValue)
})

tab.value = route.params.tab
</script>
