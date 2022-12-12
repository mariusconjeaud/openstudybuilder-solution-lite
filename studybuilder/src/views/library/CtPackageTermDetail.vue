<template>
<package-timeline
  :catalogue_name="$route.params.catalogue_name"
  :packageName="$route.params.package_name"
  @catalogueChanged="updateCatalogue"
  @packageChanged="updateTerms"
  >
  <template v-slot:default="{ selectedPackage }">
    <div class="page-title">
      {{ $t('CodelistTermsView.codelist') }} {{ $route.params.codelist_id }} - {{ codelistAttributes.submissionValue }} / {{ $t('CodelistTermDetail.term_detail') }} ({{ $t('CodelistTermDetail.concept_id') }}: {{ $route.params.termId }})
    </div>
    <codelist-term-detail
      :codelistUid="$route.params.codelist_id"
      :termUid="$route.params.term_id"
      :packageName="selectedPackage"
      />
  </template>
</package-timeline>
</template>

<script>
import controlledTerminology from '@/api/controlledTerminology'
import CodelistTermDetail from '@/components/library/CodelistTermDetail'
import PackageTimeline from '@/components/library/PackageTimeline'

export default {
  components: {
    CodelistTermDetail,
    PackageTimeline
  },
  data () {
    return {
      codelistAttributes: {}
    }
  },
  methods: {
    updateCatalogue (catalogueName) {
      this.$router.push({
        name: 'CtPackages',
        params: { catalogue_name: catalogueName }
      })
    },
    updateTerms (catalogueName, packageName) {
      this.$router.push({
        name: 'CtPackageTerms',
        params: {
          codelist_id: this.$route.params.codelist_id,
          catalogue_name: catalogueName,
          package_name: packageName
        }
      })
    }
  },
  mounted () {
    this.$store.dispatch('app/addBreadcrumbsLevel', {
      text: this.$route.params.termId,
      index: 7
    })
    controlledTerminology.getCodelistAttributes(this.$route.params.codelist_id).then(resp => {
      this.codelistAttributes = resp.data
    })
  }
}
</script>
