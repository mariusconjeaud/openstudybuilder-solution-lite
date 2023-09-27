<template>
<package-timeline
  :catalogue-name="catalogueName"
  :package-name="packageName"
  @catalogueChanged="updateUrl"
  @packageChanged="updateUrl"
  >
  <template v-slot:default="{ catalogue_name, selectedPackage }">
    <codelist-table
      :catalogue="catalogue_name"
      :package="selectedPackage"
      table-height="50vh"
      read-only
      @openCodelistTerms="openCodelistTerms"
      column-data-resource="ct/codelists"
      :terms="terms"
      :loading="loading"
      >
      <template v-slot:extraActions>
        <v-btn
          class="mx-2"
          fab
          small
          @click="goToPackagesHistory(catalogue_name)"
          :title="$t('CtPackageHistory.ct_packages_history')"
          >
          <v-icon>mdi-calendar-clock</v-icon>
        </v-btn>
      </template>
    </codelist-table>
  </template>
</package-timeline>
</template>

<script>
import CodelistTable from './CodelistTable'
import PackageTimeline from './PackageTimeline'
import controlledTerminology from '@/api/controlledTerminology'

export default {
  props: ['catalogueName', 'packageName'],
  components: {
    CodelistTable,
    PackageTimeline
  },
  data () {
    return {
      terms: [],
      loading: false
    }
  },
  methods: {
    openCodelistTerms ({ codelist, catalogueName, packageName }) {
      this.$router.push({
        name: 'CtPackageTerms',
        params: {
          codelist_id: codelist.codelist_uid,
          catalogue_name: catalogueName,
          package_name: packageName
        }
      })
    },
    updateUrl (catalogueName, packageName) {
      this.$router.push({
        name: 'CtPackages',
        params: { catalogue_name: catalogueName, package_name: packageName }
      })
    },
    goToPackagesHistory (catalogueName) {
      this.$router.push({
        name: 'CtPackagesHistory',
        params: { catalogue_name: catalogueName }
      })
    },
    fetchTerms  () {
      this.loading = true
      const params = {
        page_size: 0,
        compact_response: true
      }
      controlledTerminology.getCodelistTermsNames(params).then(resp => {
        this.terms = resp.data.items
        this.loading = false
      })
    }
  },
  mounted () {
    this.fetchTerms()
  }
}
</script>
