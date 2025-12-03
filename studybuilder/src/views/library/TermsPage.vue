<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('CodelistTermsView.terms_listing') }}
      <HelpButton :help-text="$t('_help.CtTermsTable.general')" />
    </div>
    <TermTable />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import { useRoute } from 'vue-router'
import TermTable from '@/components/library/TermTable.vue'
import HelpButton from '@/components/tools/HelpButton.vue'

const { t } = useI18n()
const appStore = useAppStore()
const route = useRoute()

onMounted(() => {
  appStore.addBreadcrumbsLevel(
    route.params.codelist_id,
    { name: 'CodeListDetail', params: route.params },
    4
  )
  appStore.addBreadcrumbsLevel(t('CodelistTermsView.terms'), {
    name: 'CodelistTerms',
    params: route.params,
  })
})
</script>
