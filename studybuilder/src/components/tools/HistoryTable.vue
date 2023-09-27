<template>
<v-card data-cy="version-history-window">
  <v-card-title>
    <span class="dialog-title">{{ title }}</span>
    <v-spacer/>
    <data-table-export-button
      v-if="withExport"
      :headers="cleanedHeaders"
      :items="items"
      :object-label="exportFullName"
      @export="(resolve) => resolve(true)"
      />
  </v-card-title>
  <v-card-text>
    <v-data-table
      :headers="cleanedHeaders"
      :items="items"
      :options.sync="options"
      :server-items-length="itemsTotal"
      dense
      >
      <template v-slot:item="{ item }">
        <tr>
          <td v-for="(header, index)  in cleanedHeaders" v-bind:key="index" :class="getTextClass(item)">
            <div :class="getCellClasses(header, item)">
              <span v-if="htmlFields && htmlFields.indexOf(header.value) !== -1" v-html="getDisplay(item, header.value)" />
              <span v-else>{{ getDisplay(item, header.value) }}</span>
            </div>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card-text>
  <v-card-actions v-if="!simpleStyling">
    <v-row>
      <v-col>
        <div>{{ $t('HistoryTable.legend') }}</div>
        <div class="ml-2 font-weight-black">{{ $t('HistoryTable.current_version') }}</div>
        <div class="ml-2">{{ $t('HistoryTable.older_version') }}</div>
        <div class="ml-2 red--text">{{ $t('HistoryTable.deleted_version') }}</div>
        <div class="ml-2 blue lighten-4 difference">{{ $t('HistoryTable.changed_value') }}</div>
      </v-col>
    </v-row>
  </v-card-actions>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn
      color="secondary"
      data-cy="close-button"
      @click="$emit('close')"
      >
      {{ $t('_global.close') }}
    </v-btn>
  </v-card-actions>
</v-card>
</template>

<script>
import DataTableExportButton from '@/components/tools/DataTableExportButton'
import { DateTime } from 'luxon'

export default {
  components: {
    DataTableExportButton
  },
  props: {
    headers: Array,
    excludedHeaders: {
      type: Array,
      required: false
    },
    items: Array,
    itemsTotal: Number,
    title: String,
    withExport: {
      type: Boolean,
      default: true
    },
    exportName: {
      type: String,
      required: false
    },
    htmlFields: {
      type: Array,
      required: false
    },
    startDateHeader: {
      type: String,
      default: 'start_date'
    },
    endDateHeader: {
      type: String,
      default: 'end_date'
    },
    changeField: {
      type: String,
      default: 'change_type'
    },
    changeFieldLabel: {
      type: String,
      required: false
    },
    simpleStyling: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      options: {}
    }
  },
  computed: {
    cleanedHeaders () {
      let result = []
      const excludedHeaders = ['actions', 'user_initials', 'start_date']
      if (this.excludedHeaders) {
        for (const header of this.excludedHeaders) {
          excludedHeaders.push(header)
        }
      }
      for (const header of this.headers) {
        if (header.historyHeader) {
          header.value = header.historyHeader
        }
      }
      result = this.headers.filter(item => {
        return !excludedHeaders.includes(item.value)
      })
      result.push({
        text: this.changeFieldLabel ? this.changeFieldLabel : this.$t('HistoryTable.change_type'),
        value: this.changeField
      })
      result.push({
        text: this.$t('_global.user'),
        value: 'user_initials'
      })
      result.push({
        text: this.$t('HistoryTable.start_date'),
        value: this.startDateHeader
      })
      result.push({
        text: this.$t('HistoryTable.end_date'),
        value: this.endDateHeader
      })
      return result
    },
    exportFullName () {
      let result = ''
      if (this.exportName) {
        result = this.exportName + '_'
      }
      result += 'history'
      return result
    }
  },
  methods: {
    getHighlight (header, item) {
      if (item) {
        if (header.value.indexOf('date') !== -1 || header.value.indexOf('change_type') !== -1) {
          return false
        } else if (item.changes) {
          if (header.value.indexOf('.') !== -1) {
            return item.changes[header.value.substring(0, header.value.indexOf('.'))]
          } else {
            return item.changes[header.value]
          }
        } else {
          return false
        }
      }
    },
    getCellClasses (header, item) {
      if (this.simpleStyling) {
        return 'ml-3'
      }
      if (this.getHighlight(header, item)) {
        return 'blue lighten-4 difference ml-3'
      }
      return 'ml-3'
    },
    getTextClass (item) {
      if (this.simpleStyling) {
        return ''
      }
      if (item.change_type === 'Delete') {
        return 'red--text'
      } else if (!item.end_date) {
        return 'font-weight-black'
      } else {
        return ''
      }
    },
    getDisplay (item, accessor) {
      const accessList = accessor.split('.')
      if (item) {
        let value = item
        for (const i in accessList) {
          const label = accessList[i]
          if (value) {
            value = value[label]
          }
        }
        if (accessor.toLowerCase().indexOf('date') !== -1) {
          if (value) {
            value = DateTime.fromISO(value).setLocale('en').toLocaleString(DateTime.DATETIME_MED)
          }
        }
        return value
      }
    }
  },
  watch: {
    options (value) {
      this.$emit('refresh', value)
    }
  }
}
</script>
