<template>
<simple-form-dialog
  ref="form"
  :title="$t('CrfTree.link') + ' ' + itemsTypeName"
  :help-items="helpItems"
  @close="close"
  @submit="submit"
  :open="open"
  maxWidth="1200px"
  >
  <template v-slot:body>
    <v-data-table
      :headers="choosenItemsheaders"
      :items="choosenItems"
      >
      <template v-slot:item.delete="{ item }">
        <v-btn
          icon
          class="mt-1 rightButtons"
          @click="removeItem(item)"
          data-cy="remove-item-link">
          <v-icon dark>
              mdi-trash-can
          </v-icon>
        </v-btn>
      </template>
    </v-data-table>
    <v-col class="pt-0 mt-0">
      <n-n-table
        :headers="availableItemsHeaders"
        item-key="uid"
        :items="items"
        has-api
        hide-export-button
        hide-default-switches
        column-data-resource="ct/codelists"
        additional-margin
        :options.sync="options"
        :server-items-length="total"
        @filter="getItems">
          <template v-slot:item.desc="{ item }">
            <div v-html="getDescription(item)"></div>
          </template>
          <template v-slot:item.notes="{ item }">
            <div v-html="getNotes(item)"></div>
          </template>
          <template v-slot:item.add="{ item }">
            <v-btn
              icon
              class="mt-1 rightButtons"
              data-cy="add-item-link"
              @click="addItem(item)"
              :disabled="checkIfLinked(item)"
              >
              <v-icon dark>
                  mdi-plus
              </v-icon>
            </v-btn>
          </template>
      </n-n-table>
    </v-col>
  </template>
</simple-form-dialog>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import crfs from '@/api/crfs'
import constants from '@/constants/parameters'
import NNTable from '@/components/tools/NNTable'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    SimpleFormDialog,
    NNTable
  },
  props: {
    itemToLink: Object,
    itemsType: String,
    open: Boolean
  },
  computed: {
    itemsTypeName () {
      return this.itemsType === 'forms' ? this.$t('CrfTree.forms') : (this.itemsType === 'item-groups' ? this.$t('CrfTree.item_groups') : this.$t('CrfTree.items'))
    }
  },
  data () {
    return {
      helpItems: [],
      items: [],
      choosenItems: [],
      choosenItemsheaders: [
        { text: this.$t('_global.name'), value: 'name' },
        { text: '', value: 'delete' }
      ],
      availableItemsHeaders: [
        { text: this.$t('_global.name'), value: 'name', width: '25%' },
        { text: this.$t('_global.description'), value: 'desc', width: '35%' },
        { text: this.$t('CrfTree.impl_notes'), value: 'notes', width: '35%' },
        { text: '', value: 'add', width: '5%' }
      ],
      options: {},
      total: 0
    }
  },
  methods: {
    getDescription (item) {
      const engDesc = item.descriptions.find(el => el.language === constants.ENG)
      return engDesc ? engDesc.description : ''
    },
    getNotes (item) {
      const engDesc = item.descriptions.find(el => el.language === constants.ENG)
      return engDesc ? engDesc.sponsor_instruction : ''
    },
    submit () {
      const payload = []
      this.choosenItems.forEach((el, index) => {
        payload.push({
          uid: el.uid ? el.uid : el,
          order_number: index,
          mandatory: el.mandatory ? el.mandatory : false,
          data_entry_required: el.data_entry_required ? el.data_entry_required : 'No',
          sdv: el.sdv ? el.sdv : 'No',
          collection_exception_condition_oid: el.collection_exception_condition_oid ? el.collection_exception_condition_oid : null,
          vendor: { attributes: [] }
        })
      })
      switch (this.itemsType) {
        case 'forms':
          crfs.addFormsToTemplate(payload, this.itemToLink.uid, true).then(resp => {
            this.$emit('close')
          })
          return
        case 'item-groups':
          crfs.addItemGroupsToForm(payload, this.itemToLink.uid, true).then(resp => {
            this.$emit('close')
          })
          return
        case 'items':
          payload.forEach(el => {
            el.key_sequence = el.key_sequence ? el.key_sequence : constants.NULL
            el.method_oid = el.method_oid ? el.method_oid : constants.NULL
            el.imputation_method_oid = el.imputation_method_oid ? el.imputation_method_oid : constants.NULL
            el.role = el.role ? el.role : constants.NULL
            el.role_codelist_oid = el.role_codelist_oid ? el.role_codelist_oid : constants.NULL
          })
          crfs.addItemsToItemGroup(payload, this.itemToLink.uid, true).then(resp => {
            this.$emit('close')
          })
      }
    },
    addItem (item) {
      if (!this.choosenItems.some(el => el.uid === item.uid)) {
        this.choosenItems.push(item)
      }
    },
    checkIfLinked (item) {
      return this.choosenItems.some(el => el.uid === item.uid)
    },
    removeItem (item) {
      this.choosenItems = this.choosenItems.filter(el => el.uid !== item.uid)
    },
    close () {
      this.form = {}
      this.choosenItems = []
      this.items = []
      this.$emit('cancel')
    },
    initForm () {
      this.choosenItems = Array.from(new Set(this.itemToLink.forms || this.itemToLink.item_groups || this.itemToLink.items))
      this.getItems()
    },
    getItems (filters, sort, filtersUpdated) {
      if (this.itemsType) {
        const parameters = filteringParameters.prepareParameters(
          this.options, filters, sort, filtersUpdated)
        if (filters) {
          parameters.filters = JSON.parse(filters)
        }
        const params = {}
        params.params = parameters
        crfs.get(this.itemsType, params).then((resp) => {
          this.items = resp.data.items
          this.total = resp.data.total
        })
      }
    }
  },
  mounted () {
    this.initForm()
  },
  watch: {
    itemToLink () {
      this.initForm()
    }
  }
}
</script>
<style scoped>
  .rightButtons {
    float: right;
  }
</style>
