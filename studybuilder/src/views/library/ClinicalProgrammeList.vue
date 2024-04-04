<template>
  <div>
    <n-n-table
      :headers="headers"
      :items="items"
      :options.sync="options"
      :server-items-length="total"
      only-text-search
      @filter="fetchProgrammes"
      hide-default-switches
      item-key="name">
      <template v-slot:actions="">
      <slot name="extraActions"></slot>
      <v-btn
        fab
        dark
        small
        color="primary"
        data-cy="add-clinical-programme"
        @click.stop="showForm"
        :title="$t('ClinicalProgrammeForm.title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    </n-n-table>
    <clinical-programme-form
      :open="showClinicalProgrammeForm"
      @close="closeForm"/>
  </div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import programmes from '@/api/clinicalProgrammes'
import ClinicalProgrammeForm from '@/components/library/ClinicalProgrammeForm'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    NNTable,
    ClinicalProgrammeForm
  },
  data () {
    return {
      headers: [
        { text: this.$t('ClinicalProgrammes.name'), value: 'name' }
      ],
      items: [],
      options: {},
      total: 0,
      filters: '',
      showClinicalProgrammeForm: false
    }
  },
  methods: {
    fetchProgrammes (filters, sort, filtersUpdated) {
      if (!filters && this.filters) {
        filters = this.filters
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      this.filters = filters
      programmes.get(params).then(resp => {
        this.items = resp.data.items
        this.total = resp.data.total
      })
    },
    showForm () {
      this.showClinicalProgrammeForm = true
    },
    closeForm () {
      this.showClinicalProgrammeForm = false
      this.fetchProgrammes()
    }
  },
  watch: {
    options () {
      this.fetchProgrammes()
    }
  }
}
</script>
