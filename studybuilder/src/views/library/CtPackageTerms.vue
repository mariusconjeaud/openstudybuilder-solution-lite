<template>
<package-timeline
  @catalogueChanged="updateCatalogue"
  @packageChanged="updateTerms"
  :catalogue_name="$route.params.catalogue_name"
  :packageName="$route.params.package_name"
  >
  <template v-slot:default="{ selectedPackage }">
    <div class="page-title">
      {{ $t('CodelistTermsView.codelist') }} {{ $route.params.codelist_id }} - {{ codelistAttributes.submission_value }} / {{ $t('CodelistTermsView.terms_listing') }}
    </div>
    <codelist-term-table
      :catalogue_name="$route.params.catalogue_name"
      :codelist_uid="$route.params.codelist_id"
      :packageName="selectedPackage"
      />
  </template>
</package-timeline>
</template>

<script>
import { mapActions } from 'vuex'
import controlledTerminology from '@/api/controlledTerminology'
import CodelistTermTable from '@/components/library/CodelistTermTable'
import PackageTimeline from '@/components/library/PackageTimeline'

export default {
  components: {
    CodelistTermTable,
    PackageTimeline
  },
  data () {
    return {
      codelistAttributes: {}
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
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
    this.addBreadcrumbsLevel({
      text: this.$route.params.codelist_id,
      to: { name: 'CtPackages', params: this.$route.params },
      index: 5
    })
    this.addBreadcrumbsLevel({
      text: this.$t('CodelistTermsView.terms'),
      to: { name: 'CtPackageTerms', params: this.$route.params }
    })
    controlledTerminology.getCodelistAttributes(this.$route.params.codelist_id).then(resp => {
      this.codelistAttributes = resp.data
    })
  },
  watch: {
    '$route.params.package_name' (value) {
      if (value) {
        const to = { name: 'CtPackages', params: { catalogue_name: this.$route.params.catalogue_name, package_name: value } }
        this.addBreadcrumbsLevel({ text: value, to, index: 4, replace: true })
      } else {
        this.$store.commit('app/TRUNCATE_BREADCRUMBS_FROM_LEVEL', 4)
      }
    }
  }

}
</script>
