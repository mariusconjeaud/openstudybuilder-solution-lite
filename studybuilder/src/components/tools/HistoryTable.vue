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
      dense
      >
      <template v-slot:item="{ item }">
        <tr>
          <td v-for="(header, index)  in cleanedHeaders" v-bind:key="index">
             <div v-if="getHighlight(index, header, item)" class="blue lighten-4 difference">{{ getDisplay(item, header.value) }}</div>
             <span v-else>{{ getDisplay(item, header.value) }}</span>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card-text>
  <v-card-actions>
    <div class="blue lighten-4 difference">{{ $t('HistoryTable.legend') }}</div>
    <v-spacer></v-spacer>
    <v-btn
      color="secondary"
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
    title: String,
    withExport: {
      type: Boolean,
      default: true
    },
    exportName: {
      type: String,
      required: false
    }
  },
  computed: {
    cleanedHeaders () {
      let result = []
      const excludedHeaders = ['actions', 'start_date']
      if (this.excludedHeaders) {
        for (const header of this.excludedHeaders) {
          excludedHeaders.push(header)
        }
      }
      result = this.headers.filter(item => {
        return !excludedHeaders.includes(item.value)
      })
      result.push({
        text: this.$t('HistoryTable.change_type'),
        value: 'change_type'
      })
      result.push({
        text: this.$t('_global.user'),
        value: 'user_initials'
      })
      result.push({
        text: this.$t('HistoryTable.start_date'),
        value: 'start_date'
      })
      result.push({
        text: this.$t('HistoryTable.end_date'),
        value: 'end_date'
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
    getHighlight (index, header, item) {
      if (item) {
        if (header.value.indexOf('Date') !== -1 || header.value.indexOf('changeType') !== -1) {
          return false
        } else if (item.changes) {
          return item.changes[header.value]
        } else {
          return false
        }
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
  }
}
</script>
