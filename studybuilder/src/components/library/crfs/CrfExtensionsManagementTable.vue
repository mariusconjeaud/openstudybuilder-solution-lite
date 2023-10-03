<template>
<div>
  <v-data-table
    :headers="selectedExtensionsHeaders"
    :items="selectedExtensions">
    <template v-slot:item.parent="{ item }">
        {{ item.vendor_namespace ? item.vendor_namespace.name : (item.vendor_element ? item.vendor_element.name : '') }}
    </template>
    <template v-slot:item.value="{ index }">
      <v-text-field
        v-model="selectedExtensions[index].value"
        :label="$t('_global.value')"
        dense
        class="mt-3"
        :readonly="readOnly">
      </v-text-field>
    </template>
    <template v-slot:item.delete="{ item }">
      <v-btn
        icon
        class="mt-1"
        :disabled="readOnly"
        @click="removeExtension(item)">
        <v-icon dark>
          mdi-delete-outline
        </v-icon>
      </v-btn>
    </template>
  </v-data-table>
  <v-row>
    <v-col class="pt-0 mt-0">
      <n-n-table
        :headers="extensionsHeaders"
        item-key="uid"
        :items="elements"
        hide-export-button
        only-text-search
        hide-default-switches
        additional-margin
        :options.sync="options"
        has-api
        @filter="getExtensionData">
        <template v-slot:item="{ item, expand, isExpanded }">
          <tr :style="item.type === 'Element' ? 'background-color: var(--v-dfltBackgroundLight1-base)' : ''">
            <td width="15%">
              <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
                <v-icon dark>
                  mdi-chevron-down
                </v-icon>
              </v-btn>
              <v-btn @click="expand(!isExpanded)" v-if="!isExpanded && item.type === 'Element'" icon>
                <v-icon dark>
                  mdi-chevron-right
                </v-icon>
              </v-btn>
            </td>
            <td width="25%">{{ item.name }}</td>
            <td width="20%">{{ item.vendor_namespace ? item.vendor_namespace.name : '' }}</td>
            <td width="20%">{{ item.data_type }}</td>
            <td width="20%">
              <v-btn
                icon
                :disabled="readOnly"
                @click="addExtension(item)">
                <v-icon dark>
                  mdi-plus
                </v-icon>
              </v-btn>
            </td>
          </tr>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td :colspan="headers.length" class="pa-0">
            <v-data-table
              :headers="extensionsHeaders"
              :items="item.vendor_attributes"
              light
              hide-default-footer
              hide-default-header>
              <template v-slot:item="{ item }">
                <tr class="attributeBackground">
                  <td width="15%"/>
                  <td width="25%">{{ item.name }}</td>
                  <td width="20%">{{ item.vendor_namespace ? item.vendor_namespace.name : '' }}</td>
                  <td width="20%">{{ item.data_type }}</td>
                  <td width="20%">
                    <v-btn
                      icon
                      :disabled="readOnly"
                      @click="addExtension(item)">
                      <v-icon dark>
                        mdi-plus
                      </v-icon>
                    </v-btn>
                  </td>
                </tr>
              </template>
            </v-data-table>
          </td>
        </template>
      </n-n-table>
    </v-col>
  </v-row>
</div>
</template>

<script>
import crfs from '@/api/crfs'
import NNTable from '@/components/tools/NNTable'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    NNTable
  },
  data () {
    return {
      attributes: [],
      elements: [],
      selectedExtensions: [],
      extensionsHeaders: [
        { text: '', value: 'data-table-expand' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('CrfExtensions.namespace'), value: 'vendor_namespace.name' },
        { text: this.$t('CrfExtensions.data_type'), value: 'data_type' },
        { text: '', value: 'add' }
      ],
      selectedExtensionsHeaders: [
        { text: this.$t('CrfExtensions.namespace'), value: 'vendor_namespace.name' },
        { text: this.$t('CrfExtensions.parent'), value: 'parent' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.type'), value: 'type' },
        { text: this.$t('CrfExtensions.data_type'), value: 'data_type' },
        { text: this.$t('_global.value'), value: 'value' },
        { text: '', value: 'delete' }
      ],
      options: {}
    }
  },
  props: {
    type: String,
    readOnly: Boolean,
    editExtensions: Array,
    onlyAttributes: {
      type: Boolean,
      default: false
    }
  },
  async mounted () {
    await this.getExtensionData()
    if (this.editExtensions) {
      this.selectedExtensions = this.editExtensions
    }
  },
  methods: {
    addExtension (item) {
      if (!this.selectedExtensions.some(el => el.uid === item.uid)) {
        this.selectedExtensions.push(item)
        if (item.vendor_element) {
          const parentElement = this.elements.find(el => el.uid === item.vendor_element.uid)
          if (parentElement && !this.selectedExtensions.some(el => el.uid === parentElement.uid)) {
            this.selectedExtensions.push(parentElement)
          }
        }
      }
    },
    removeExtension (item) {
      this.selectedExtensions = this.selectedExtensions.filter(el => el.uid !== item.uid)
      if (item.type === 'Element') {
        this.selectedExtensions = this.selectedExtensions.filter(el => el.vendor_element ? el.vendor_element.uid !== item.uid : el)
      }
      this.$emit('setExtensions', this.selectedExtensions)
    },
    async getExtensionData (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      if (!this.onlyAttributes) {
        await this.getElements(params)
        this.elements.forEach((el, index) => {
          this.getAttributes(el, index)
        })
        await this.getAttributesWithNoParent(params)
        this.elements = [...this.elements, ...this.attributes]
      } else {
        await this.getAttributesWithNoParent(params)
        this.elements = this.attributes
      }
    },
    async getElements (params) {
      await crfs.getAllElements(params).then(resp => {
        this.elements = resp.data.items
        this.elements.forEach(el => {
          el.type = 'Element'
        })
      })
    },
    async getAttributes (element, index) {
      const attributes = element.vendor_attributes.map(attr => attr.uid)
      const params = {
        filters: { uid: { v: attributes, op: 'co' } }
      }
      await crfs.getAllAttributes(params).then(resp => {
        resp.data.items.forEach(el => {
          el.type = 'Attribute'
          el.vendor_namespace = element.vendor_namespace
        })
        this.elements[index].vendor_attributes = resp.data.items
      })
    },
    async getAttributesWithNoParent (params) {
      if (params.filters) {
        params.filters = JSON.parse(params.filters)
        params.filters.vendor_element = { v: [], op: 'co' }
        params.filters.compatible_types = { v: [this.type], op: 'co' }
      } else {
        params.filters = { vendor_element: { v: [], op: 'co' }, compatible_types: { v: [this.type], op: 'co' } }
      }
      await crfs.getAllAttributes(params).then(resp => {
        resp.data.items.forEach(el => {
          el.type = 'Attribute'
        })
        this.attributes = resp.data.items
      })
    }
  },
  watch: {
    editExtensions (value) {
      if (value) {
        this.selectedExtensions = value
      }
    }
  }
}
</script>
<style scoped>
.attributeBackground {
  background-color: var(--v-dfltBackgroundLight2-base)
}
</style>
