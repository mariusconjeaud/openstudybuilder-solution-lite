<template>
<div class="px-4">
  <div class="page-title">
    {{ codelistAttributes.name }} ({{ $route.params.codelist_id }}) - {{ codelistAttributes.submission_value }} / {{ $t('CodelistTermsView.terms_listing') }}
  </div>
  <codelist-term-table
    :catalogue-name="$route.params.catalogue_name"
    :codelist-uid="$route.params.codelist_id"
    />
</div>
</template>

<script>
import { mapActions } from 'vuex'
import controlledTerminology from '@/api/controlledTerminology'
import CodelistTermTable from '@/components/library/CodelistTermTable'

export default {
  components: {
    CodelistTermTable
  },
  data () {
    return {
      codelistAttributes: {}
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    })
  },
  mounted () {
    this.addBreadcrumbsLevel({
      text: this.$route.params.codelist_id,
      to: { name: 'CodeListDetail', params: this.$route.params },
      index: 4
    })
    this.addBreadcrumbsLevel({
      text: this.$t('CodelistTermsView.terms'),
      to: { name: 'CodelistTerms', params: this.$route.params }
    })
    controlledTerminology.getCodelistAttributes(this.$route.params.codelist_id).then(resp => {
      this.codelistAttributes = resp.data
    })
  }
}
</script>
