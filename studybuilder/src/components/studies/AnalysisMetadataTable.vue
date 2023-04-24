<template>
<n-n-table
  @filter="fetchData"
  :headers="headers"
  item-key="uid"
  :server-items-length="total"
  :options.sync="options"
  :items="items"
  show-column-names-toggle-button
  :export-data-url="exportDataUrl"
  :export-object-label="exportObjectLabel"
  has-api
  :column-data-resource="exportDataUrl"
  >
  <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
    <slot :name="slot" v-bind="scope" v-bind:showSelectBoxes="showSelectBoxes" />
  </template>
</n-n-table>
</template>

<script>
import filteringParameters from '@/utils/filteringParameters'
import listings from '@/api/listings'
import { mapGetters } from 'vuex'
import NNTable from '@/components/tools/NNTable'

export default {
  components: {
    NNTable
  },
  props: {
    type: String,
    headers: Array
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    exportDataUrl () {
      return `listings/studies/${this.selectedStudy.uid}/adam/${this.type}`
    },
    exportObjectLabel () {
      return `adam-${this.type}`
    }
  },
  data () {
    return {
      items: [],
      options: {},
      total: 0
    }
  },
  methods: {
    fetchData (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      listings.getAllAdam(this.selectedStudy.uid, this.type, params).then(resp => {
        this.items = resp.data.items
        this.total = resp.data.total
      })
    }
  },
  watch: {
    options () {
      this.fetchData()
    }
  }
}
</script>
