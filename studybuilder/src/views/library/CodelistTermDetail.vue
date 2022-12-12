<template>
<div class="px-4">
  <div class="page-title">
    {{ $t('CodelistTermsView.codelist') }} {{ $route.params.codelist_id }} - {{ codelistAttributes.submission_value }} / {{ $t('CodelistTermDetail.term_detail') }} ({{ $t('CodelistTermDetail.concept_id') }}: {{ $route.params.term_id }})
  </div>
  <codelist-term-detail
    :codelist-uid="$route.params.codelist_id"
    :term-uid="$route.params.term_id"
    />
</div>
</template>

<script>
import controlledTerminology from '@/api/controlledTerminology'
import CodelistTermDetail from '@/components/library/CodelistTermDetail'

export default {
  components: {
    CodelistTermDetail
  },
  data () {
    return {
      codelistAttributes: {}
    }
  },
  mounted () {
    this.$store.dispatch('app/addBreadcrumbsLevel', {
      text: this.$route.params.term_id,
      index: 6
    })
    controlledTerminology.getCodelistAttributes(this.$route.params.codelist_id).then(resp => {
      this.codelistAttributes = resp.data
    })
  }
}
</script>
