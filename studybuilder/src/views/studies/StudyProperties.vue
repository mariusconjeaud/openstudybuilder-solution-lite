<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('Sidebar.study.study_properties') }} ({{ studyId }})
      <HelpButtonWithPanels
        :help-text="$t('_help.StudyProperties.general')"
        :items="helpItems"
      />
    </div>
    <v-tabs v-model="tab" bg-color="white">
      <v-tab v-for="item of tabs" :key="item.tab" :value="item.tab">
        {{ item.name }}
      </v-tab>
    </v-tabs>
    <v-window v-model="tab">
      <v-window-item value="type">
        <StudyTypeSummary :key="`type-${tabKeys.type}`" />
      </v-window-item>
      <v-window-item value="attributes">
        <InterventionTypeSummary :key="`attributes-${tabKeys.attributes}`" />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels.vue'
import InterventionTypeSummary from '@/components/studies/InterventionTypeSummary.vue'
import StudyTypeSummary from '@/components/studies/StudyTypeSummary.vue'
import { useAppStore } from '@/stores/app'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useTabKeys } from '@/composables/tabKeys'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const appStore = useAppStore()
const studiesGeneralStore = useStudiesGeneralStore()
const { tabKeys, updateTabKey } = useTabKeys()

const helpItems = ['StudyProperties.study_type']
const tabs = [
  { tab: 'type', name: t('Sidebar.study.study_type') },
  { tab: 'attributes', name: t('Sidebar.study.study_attributes') },
]

const tab = ref(null)

const selectedStudy = computed(() => studiesGeneralStore.selectedStudy)
const studyId = computed(() => studiesGeneralStore.studyId)

watch(tab, (newValue) => {
  router.push({
    name: 'StudyProperties',
    params: { tab: newValue },
  })
  const tabName = newValue
    ? tabs.find((el) => el.tab === newValue).name
    : tabs[0].name
  appStore.addBreadcrumbsLevel(
    tabName,
    {
      name: 'StudyProperties',
      params: { study_id: selectedStudy.value.uid, tab: tabName },
    },
    3,
    true
  )
  updateTabKey(newValue)
})

onMounted(() => {
  tab.value = route.params.tab || tabs[0].tab
  const tabName = tab.value
    ? tabs.find((el) => el.tab === tab.value).name
    : tabs[0].name
  setTimeout(() => {
    appStore.addBreadcrumbsLevel(
      tabName,
      {
        name: 'StudyProperties',
        params: { study_id: selectedStudy.value.uid, tab: tabName },
      },
      3,
      true
    )
  }, 100)
})
</script>
