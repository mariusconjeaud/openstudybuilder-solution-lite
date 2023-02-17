<template>
<n-n-table
  v-model="selected"
  :headers="headers"
  :items="templates"
  item-key="uid"
  :export-object-label="objectType"
  :export-data-url="urlPrefix"
  :server-items-length="total"
  sort-by="start_date"
  sort-desc
  :options.sync="options"
  :has-api="hasApi"
  :column-data-resource="columnDataResource"
  :column-data-parameters="extendedColumnDataParameters"
  @filter="filter"
  >
  <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
    <slot :name="slot" v-bind="scope" />
  </template>
  <template v-slot:item.name="{ item }">
    <n-n-parameter-highlighter :name="item.name" default-color="orange" />
  </template>
  <template v-slot:item.start_date="{ item }">
    {{ item.start_date | date }}
  </template>
  <template v-slot:item.status="{ item }">
    <status-chip :status="item.status" />
  </template>
</n-n-table>
</template>

<script>
import libraryConstants from '@/constants/libraries'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import NNTable from '@/components/tools/NNTable'
import templates from '@/api/templates'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    NNParameterHighlighter,
    NNTable
  },
  props: {
    urlPrefix: {
      type: String,
      default: ''
    },
    translationType: {
      type: String,
      default: ''
    },
    objectType: {
      type: String,
      default: ''
    },
    hasApi: {
      type: Boolean,
      default: false
    },
    columnDataResource: {
      type: String,
      default: ''
    },
    exportDataUrlParams: {
      type: Object,
      required: false
    }
  },
  data () {
    return {
      headers: [
        { text: this.$t('_global.template'), value: 'name', width: '70%', filteringName: 'name_plain' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      options: {},
      selected: [],
      templates: [],
      total: 0,
      api: null
    }
  },
  computed: {
    extendedColumnDataParameters () {
      const result = this.columnDataParameters ? { ...this.columnDataParameters } : { filters: {} }
      result.filters['library.name'] = { v: [libraryConstants.LIBRARY_USER_DEFINED] }
      return result
    }
  },
  created () {
    this.api = templates(this.urlPrefix)
  },
  methods: {
    async filter (filters, sort, filtersUpdated) {
      filters = (filters) ? JSON.parse(filters) : {}
      filters['library.name'] = { v: [libraryConstants.LIBRARY_USER_DEFINED] }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      this.api.get(params).then(resp => {
        if (resp.data.items !== undefined) {
          this.templates = resp.data.items
          this.total = resp.data.total
        } else {
          this.templates = resp.data
          this.total = this.templates.length
        }
      })
    }
  },
  watch: {
    options: {
      handler () {
        this.filter()
      },
      deep: true
    }
  }
}
</script>
