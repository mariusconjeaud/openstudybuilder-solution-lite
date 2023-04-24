<template>
<div>
  <v-tabs v-model="tab">
    <v-tab v-for="catalogue in allCatalogues"
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
        library="Sponsor"
        />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import CodelistTable from './CodelistTable'

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
      tab: null
    }
  },
  mounted () {
    this.$store.dispatch('ctCatalogues/fetchCatalogues')
    setTimeout(() => {
      this.addBreadcrumbsLevel({
        text: this.tab,
        index: 3,
        replace: true
      })
    }, 100)
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    openCodelistTerms ({ codelist, catalogueName }) {
      this.$router.push({
        name: 'CodelistTerms',
        params: { codelist_id: codelist.codelist_uid, catalogue_name: catalogueName }
      })
    }
  },
  watch: {
    tab (newValue) {
      this.addBreadcrumbsLevel({
        text: newValue,
        index: 3,
        replace: true
      })
    }
  }
}
</script>
