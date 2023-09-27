<template>
<div>
  <v-tabs v-model="tab">
    <v-tab v-for="catalogue in allCatalogues"
           :data-cy="catalogue.name"
           :key="catalogue.name"
           :href="`#${catalogue.name}`"
           >
      {{ catalogue.name }}
    </v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item
      v-for="catalogue in allCatalogues"
      :key="catalogue.name"
      :id="catalogue.name"
      >
      <codelist-table
        :catalogue="catalogue.name"
        @openCodelistTerms="openCodelistTerms"
        column-data-resource="ct/codelists"
        :terms="terms"
        :loading="loading"
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import CodelistTable from './CodelistTable'
import controlledTerminology from '@/api/controlledTerminology'

export default {
  components: {
    CodelistTable
  },
  props: ['catalogue_name'],
  computed: {
    ...mapGetters({
      catalogues: 'ctCatalogues/catalogues'
    }),
    allCatalogues () {
      const array = [{ name: 'All' }]
      return array.concat(this.catalogues)
    }
  },
  data () {
    return {
      tab: null,
      originalCatalogue: null,
      terms: [],
      loading: false
    }
  },
  methods: {
    openCodelistTerms ({ codelist, catalogueName }) {
      this.$router.push({
        name: 'CodelistTerms',
        params: { codelist_id: codelist.codelist_uid, catalogue_name: catalogueName }
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
    this.originalCatalogue = this.catalogue_name
    this.$store.dispatch('ctCatalogues/fetchCatalogues')
    this.fetchTerms()
  },
  watch: {
    tab (newValue, oldValue) {
      if (newValue !== this.catalogue_name) {
        this.$store.commit('ctCatalogues/SET_CURRENT_CATALOGUE_PAGE', 1)
      }
      this.$emit('catalogueChanged', newValue)
    },
    catalogues (newValue) {
      this.tab = this.originalCatalogue
    }
  }
}
</script>
