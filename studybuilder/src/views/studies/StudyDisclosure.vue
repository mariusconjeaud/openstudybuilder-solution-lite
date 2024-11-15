<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('StudyDisclosure.study_disclosure') }}
    </div>
    <v-tabs v-model="activeTab" bg-color="white" class="topRadius elevation-4">
      <v-tab v-for="tab of tabs" :key="tab.tab" :href="tab.tab">
        {{ tab.name }}
      </v-tab>
    </v-tabs>
    <v-window v-model="activeTab" class="bg-white bottomRadius  elevation-4">
      <v-window-item value="study_disclosure">
        <StudyDisclosureTable />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'
import StudyDisclosureTable from '@/components/studies/StudyDisclosureTable.vue'

const { t } = useI18n()
  
const activeTab = ref(null)
const tabs = [
  { tab: 'study_disclosure', name: t('StudyDisclosure.tab_1') },
]

</script>
<style>
.topRadius {
  border-top-right-radius: 12px;
  border-top-left-radius: 12px;
}
.bottomRadius {
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}
</style>