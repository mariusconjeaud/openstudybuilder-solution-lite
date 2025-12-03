<template>
  <div class="px-4">
    <div class="page-title">
      {{ $t('CodelistTermDetail.term_detail') }} ({{
        $t('CodelistTermDetail.term_uid')
      }}: {{ $route.params.term_id }})
    </div>
    <CodelistTermDetail :term-uid="$route.params.term_id" />
  </div>
</template>

<script>
import CodelistTermDetail from '@/components/library/CodelistTermDetail.vue'
import { useAppStore } from '@/stores/app'

export default {
  components: {
    CodelistTermDetail,
  },
  setup() {
    const appStore = useAppStore()
    return {
      addBreadcrumbsLevel: appStore.addBreadcrumbsLevel,
    }
  },
  data() {
    return {}
  },
  mounted() {
    this.addBreadcrumbsLevel(this.$route.params.term_id, undefined, 6)
  },
}
</script>
