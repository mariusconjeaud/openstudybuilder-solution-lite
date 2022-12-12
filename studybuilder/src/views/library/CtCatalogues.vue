<template>
<div class="px-4">
  <div data-cy="page-title" class="page-title d-flex align-center">
    {{ $t('CtCataloguesView.title') }}
    <help-button :help-text="$t('_help.CtCataloguesTable.general')" />
  </div>
  <ct-catalogues-table
    :catalogue_name="$route.params.catalogue_name"
    @catalogueChanged="updateCatalogue"
    />
</div>
</template>

<script>
import { mapActions } from 'vuex'
import CtCataloguesTable from '@/components/library/CtCataloguesTable'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    CtCataloguesTable,
    HelpButton
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    updateCatalogue (catalogueName) {
      this.$router.push({
        name: 'CtCatalogues',
        params: { catalogue_name: catalogueName }
      })
    }
  },
  mounted () {
    if (this.$route.params.catalogue_name) {
      this.addBreadcrumbsLevel({
        text: this.$route.params.catalogue_name,
        to: { name: 'CtCatalogues', params: this.$route.params },
        index: 3
      })
    }
  },
  watch: {
    '$route.params.catalogue_name' (value) {
      this.addBreadcrumbsLevel({
        text: value,
        to: { name: 'CtCatalogues', params: { catalogue_name: value } },
        index: 3,
        replace: true
      })
    }
  }
}
</script>
