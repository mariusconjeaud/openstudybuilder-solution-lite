<template>
<n-n-table
  :headers="headers"
  :items="items"
  :options.sync="options"
  @filter="fetchListings"
  has-api
  :column-data-resource="`listings/libraries/all/gcmd/${source}`"
  :export-data-url="`listings/libraries/all/gcmd/${source}`"
  :server-items-length="total"
  item-key="topic_cd"
  show-column-names-toggle-button
  />
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import gcm from '@/api/generalClinicalMetadata'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    NNTable
  },
  props: {
    source: String
  },
  data () {
    return {
      headers: [
        { text: this.$t('ClinicalMetadataTable.label'), value: 'lb' },
        { text: this.$t('ClinicalMetadataTable.topic_code'), value: 'topic_cd' },
        { text: this.$t('ClinicalMetadataTable.short_topic_code'), value: 'short_topic_cd' },
        { text: this.$t('ClinicalMetadataTable.convert_to_si_unit'), value: 'convert_to_si_unit' },
        { text: this.$t('ClinicalMetadataTable.convert_to_us_conv_unit'), value: 'convert_to_us_conv_unit' },
        { text: this.$t('ClinicalMetadataTable.description'), value: 'description' },
        { text: this.$t('ClinicalMetadataTable.molecular_weight'), value: 'molecular_weight' },
        { text: this.$t('ClinicalMetadataTable.value_sas_display_format'), value: 'value_sas_display_format' },
        { text: this.$t('ClinicalMetadataTable.general_domain_class'), value: 'general_domain_class' },
        { text: this.$t('ClinicalMetadataTable.sub_domain_class'), value: 'sub_domain_class' },
        { text: this.$t('ClinicalMetadataTable.sub_domain_type'), value: 'sub_domain_type' }
      ],
      items: [],
      options: {},
      total: 0
    }
  },
  methods: {
    fetchListings (filters, sort, filtersUpdated) {
      if (this.source) {
        const params = filteringParameters.prepareParameters(
          this.options, filters, sort, filtersUpdated)
        gcm.get(this.source, params).then(resp => {
          this.items = resp.data.items
          this.total = resp.data.total
        })
      }
    }
  },
  watch: {
    options () {
      this.fetchListings()
    }
  }
}
</script>
