<template>
<div>
  <simple-form-dialog
    ref="form"
    :title="title"
    :help-items="helpItems"
    @close="cancel"
    :open="open"
    max-width="1200px"
    no-saving
    >
    <template v-slot:body>
      <n-n-table
        :headers="headers"
        item-key="uid"
        :options.sync="options"
        :server-items-length="total"
        :items="elements"
        hide-default-switches
        show-expand
        light
        sort-by="name"
        disable-filtering
        hide-export-button
        :modifiableTable="false"
        >
        <template v-slot:item="{ item, expand, isExpanded }">
          <tr style="background-color: var(--v-dfltBackgroundLight1-base)">
            <td width="1%">
              <v-btn @click="expand(!isExpanded)" v-if="isExpanded" icon>
                <v-icon dark>
                  mdi-chevron-down
                </v-icon>
              </v-btn>
              <v-btn @click="expand(!isExpanded)" v-else-if="item.attributes" icon>
                <v-icon dark>
                  mdi-chevron-right
                </v-icon>
              </v-btn>
            </td>
            <td>
              <v-row class="mt-1">
                <actions-menu :actions="actions" :item="item" />
                {{item.name}}
              </v-row>
            </td>
          </tr>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td :colspan="headers.length" class="pa-0">
          <v-data-table
            :headers="headers"
            item-key="uid"
            :options.sync="options"
            :server-items-length="total"
            :items="item.attributes"
            hide-default-switches
            light
            sort-by="name"
            disable-filtering
            hide-export-button
            :modifiableTable="false"
            hide-default-footer
            hide-default-header
            >
            <template v-slot:item="{ item }">
              <tr style="background-color: var(--v-dfltBackgroundLight2-base)">
                <td width="8%"></td>
                <td>
                  <v-row class="mt-1">
                    <actions-menu :actions="actions" :item="item"/>
                    {{item.name}}
                </v-row>
                </td>
              </tr>
            </template>
          </v-data-table>
        </td>
        </template>
        <template v-slot:actions="">
          <v-btn
            class="ml-2"
            dark
            small
            color="error"
            @click="deleteNamespace"
            v-if="editItem.status === constants.DRAFT"
            >
            <v-icon dark>
              mdi-trash-can
            </v-icon>
            {{ $t('CrfExtensions.delete_namespace') }}
          </v-btn>
          <v-btn
            class="ml-2"
            dark
            small
            color="primary"
            @click="addElement"
            >
            <v-icon dark>
              mdi-plus
            </v-icon>
            {{ $t('CrfExtensions.element') }}
          </v-btn>
          <v-btn
            class="ml-2"
            dark
            small
            color="primary"
            @click="addAttribute"
            >
            <v-icon dark>
              mdi-plus
            </v-icon>
            {{ $t('CrfExtensions.attribute') }}
          </v-btn>
        </template>
      </n-n-table>
    </template>
  </simple-form-dialog>
  <crf-attribute-form
    :open="showAttributeForm"
    @close="closeAttributeForm"
    :editItem="elementToEdit"
    />
  <crf-element-form
    :parentUid="editItem.uid"
    :open="showElementForm"
    @close="closeElementForm"
    :attributes="attributes"
    :editItem="elementToEdit"
    />
</div>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import NNTable from '@/components/tools/NNTable'
import CrfAttributeForm from '@/components/library/CrfAttributeForm'
import CrfElementForm from '@/components/library/CrfElementForm'
import crfs from '@/api/crfs'
import ActionsMenu from '@/components/tools/ActionsMenu'
import constants from '@/constants/statuses'

export default {
  components: {
    SimpleFormDialog,
    NNTable,
    CrfAttributeForm,
    CrfElementForm,
    ActionsMenu
  },
  props: {
    open: Boolean,
    editItem: Object
  },
  computed: {
    title () {
      return this.$t('CrfExtensions.extension') + this.editItem.name
    }
  },
  created () {
    this.constants = constants
  },
  data () {
    return {
      helpItems: [],
      elements: [],
      total: 0,
      options: {},
      headers: [
        { text: this.$t('_global.name'), value: 'name' }
      ],
      showAttributeForm: false,
      showElementForm: false,
      attributes: [],
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          click: this.editElement
        }
      ],
      elementToEdit: {}
    }
  },
  mounted () {
    this.getNamespaceData()
  },
  methods: {
    addElement () {
      this.showElementForm = true
    },
    closeElementForm () {
      this.showElementForm = false
      this.elementToEdit = {}
      this.getNamespaceData()
    },
    addAttribute () {
      this.showAttributeForm = true
    },
    closeAttributeForm () {
      this.showAttributeForm = false
      this.elementToEdit = {}
      this.getNamespaceData()
    },
    deleteNamespace () {
      crfs.deleteNamespace(this.editItem.uid).then(() => {
        this.close()
      })
    },
    editElement (item) {
      this.elementToEdit = item
      if (item.type === 'attr') {
        this.showAttributeForm = true
      } else {
        this.showElementForm = true
      }
    },
    cancel () {
      this.close()
    },
    close () {
      this.$emit('close')
    },
    async getAllAttributes () {
      const params = {
        page_size: 0
      }
      await crfs.getAllAttributes(params).then(resp => {
        this.attributes = resp.data.items
        this.attributes.forEach(attr => {
          attr.type = 'attr'
        })
      })
    },
    async getNamespaceData () {
      await this.getAllAttributes()
      if (this.editItem.uid) {
        crfs.getNamespace(this.editItem.uid).then((resp) => {
          if (resp.data.vendor_attributes || resp.data.vendor_elements) {
            this.elements = []
            resp.data.vendor_attributes = resp.data.vendor_attributes.map(attr => this.attributes.find(el => attr.uid === el.uid))
            resp.data.vendor_attributes.forEach(attr => {
              attr.type = 'attr'
            })
            this.elements.push(...resp.data.vendor_attributes, ...resp.data.vendor_elements)
            this.total = this.elements.length
          }
          for (const attr of this.attributes) {
            if (attr.vendor_element) {
              const index = this.elements.indexOf(this.elements.find(ele => ele.uid === attr.vendor_element.uid))
              if (this.elements[index]) {
                if (!this.elements[index].attributes) {
                  this.elements[index].attributes = []
                }
                this.elements[index].attributes.push(attr)
              }
            }
          }
        })
      }
    }
  },
  watch: {
    editItem () {
      this.getNamespaceData()
    }
  }
}
</script>
