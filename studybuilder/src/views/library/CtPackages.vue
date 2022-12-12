<template>
<div class="px-4">
  <div data-cy="page-title" class="page-title d-flex align-center">
    {{ $t('CtPackagesView.title') }}
    <help-button :help-text="$t('_help.CtPackagesTable.general')" />
  </div>
  <ct-packages-table
    :catalogue-name="$route.params.catalogue_name"
    :package-name="$route.params.package_name"
    />
</div>
</template>

<script>
import { mapActions } from 'vuex'
import CtPackagesTable from '@/components/library/CtPackagesTable'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    CtPackagesTable,
    HelpButton
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    updateCatalogueInBreadcrumbs (catalogueName, replace) {
      this.addBreadcrumbsLevel({
        text: catalogueName,
        to: { name: 'CtPackages', params: { catalogue_name: catalogueName } },
        index: 3,
        replace
      })
    },
    updatePackageInBreadcrumbs (packageName, catalogueName, replace) {
      this.addBreadcrumbsLevel({
        text: packageName,
        to: { name: 'CtPackages', params: { catalogue_name: catalogueName, package_name: packageName } },
        index: 4,
        replace
      })
    }
  },
  mounted () {
    if (this.$route.params.catalogue_name) {
      this.updateCatalogueInBreadcrumbs(this.$route.params.catalogue_name)
    }
    if (this.$route.params.package_name) {
      this.updatePackageInBreadcrumbs(this.$route.params.package_name, this.$route.params.catalogue_name)
    }
  },
  watch: {
    '$route.params.catalogue_name' (value) {
      this.updateCatalogueInBreadcrumbs(value, true)
    },
    '$route.params.package_name' (value) {
      if (value) {
        this.updatePackageInBreadcrumbs(value, this.$route.params.catalogue_name, true)
      } else {
        this.$store.commit('app/TRUNCATE_BREADCRUMBS_FROM_LEVEL', 4)
      }
    }
  }
}
</script>
