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
            <td width="10%">
              <v-row class="mt-1">
                <actions-menu :actions="actions" :item="item" />
                {{item.type ? $t('CrfExtensions.attribute') : $t('CrfExtensions.element')}}
              </v-row>
            </td>
            <td width="10%">
              {{item.name}}
            </td>
            <td width="10%">
              {{item.version}}
            </td>
            <td width="10%">
              <status-chip :status="item.status" />
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
            sort-by="name"
            disable-filtering
            hide-export-button
            :modifiableTable="false"
            hide-default-footer
            hide-default-header
            >
            <template v-slot:item="{ item }">
              <tr style="background-color: var(--v-dfltBackgroundLight2-base)">
                <td width="1%">
                  <v-btn icon>
                  </v-btn>
                </td>
                <td width="10%">
                  <v-row class="mt-1">
                    <actions-menu :actions="actions" :item="item"/>
                    {{ $t('CrfExtensions.attribute') }}
                  </v-row>
                </td>
                <td width="10%">
                  {{item.name}}
                </td>
                <td width="10%">
                  {{item.version}}
                </td>
                <td width="10%">
                  <status-chip :status="item.status" />
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
            color="crfGroup"
            rounded
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
            color="crfItem"
            rounded
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
    :parent-uid="parentUid"
    :parent-type="parentType"
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
import CrfAttributeForm from '@/components/library/crfs/CrfAttributeForm'
import CrfElementForm from '@/components/library/crfs/CrfElementForm'
import crfs from '@/api/crfs'
import ActionsMenu from '@/components/tools/ActionsMenu'
import constants from '@/constants/statuses'
import StatusChip from '@/components/tools/StatusChip'
import crfTypes from '@/constants/crfTypes'

export default {
  components: {
    SimpleFormDialog,
    NNTable,
    CrfAttributeForm,
    CrfElementForm,
    ActionsMenu,
    StatusChip
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
        { text: this.$t('_global.type'), value: 'type' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.status'), value: 'status' }
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
        },
        {
          label: this.$t('CrfExtensions.add_new_attr'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: (item) => !item.type,
          click: this.addAttribute
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.possible_actions.find(action => action === 'approve'),
          click: this.approve
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'new_version'),
          click: this.newVersion
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'inactivate'),
          click: this.inactivate
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'reactivate'),
          click: this.reactivate
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          click: this.delete
        }
      ],
      elementToEdit: {},
      parentType: '',
      parentUid: ''
    }
  },
  mounted () {
    this.getNamespaceData()
  },
  methods: {
    approve (item) {
      const type = item.type === 'attr' ? 'vendor-attributes' : 'vendor-elements'
      crfs.approve(type, item.uid).then(() => {
        this.getNamespaceData()
      })
    },
    inactivate (item) {
      const type = item.type === 'attr' ? 'vendor-attributes' : 'vendor-elements'
      crfs.inactivate(type, item.uid).then(() => {
        this.getNamespaceData()
      })
    },
    reactivate (item) {
      const type = item.type === 'attr' ? 'vendor-attributes' : 'vendor-elements'
      crfs.reactivate(type, item.uid).then(() => {
        this.getNamespaceData()
      })
    },
    async newVersion (item) {
      const type = item.type === 'attr' ? 'vendor-attributes' : 'vendor-elements'
      crfs.newVersion(type, item.uid).then(() => {
        this.getNamespaceData()
      })
    },
    addElement () {
      this.showElementForm = true
    },
    closeElementForm () {
      this.showElementForm = false
      this.elementToEdit = {}
      this.getNamespaceData()
    },
    addAttribute (item) {
      if (item.uid) {
        this.parentType = crfTypes.ELEMENT
        this.parentUid = item.uid
      } else {
        this.parentType = crfTypes.NAMESPACE
        this.parentUid = this.editItem.uid
      }
      this.showAttributeForm = true
    },
    closeAttributeForm () {
      this.showAttributeForm = false
      this.parentType = ''
      this.parentUid = ''
      this.elementToEdit = {}
      this.getNamespaceData()
    },
    editElement (item) {
      this.elementToEdit = item
      if (item.type === 'attr') {
        this.parentType = item.vendor_namespace ? crfTypes.NAMESPACE : crfTypes.ELEMENT
        this.showAttributeForm = true
      } else {
        this.showElementForm = true
      }
    },
    delete (item) {
      if (item.type) {
        crfs.delete('vendor-attributes', item.uid).then(() => {
          this.getNamespaceData()
        })
      } else {
        crfs.delete('vendor-elements', item.uid).then(() => {
          this.getNamespaceData()
        })
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
