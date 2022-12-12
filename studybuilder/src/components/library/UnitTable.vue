<template>
<div>
  <n-n-table
    :headers="headers"
    :items="units"
    item-key="uid"
    sort-by="start_date"
    sort-desc
    has-api
    export-data-url="concepts/unit-definitions"
    export-object-label="Units"
    column-data-resource="concepts/unit-definitions"
    :options.sync="options"
    :server-items-length="total"
    @filter="getUnits"
    >
    <template v-slot:actions="">
      <v-btn
        class="ml-2"
        fab
        dark
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('UnitForm.add_title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.master_unit="{ item }">
      {{ item.master_unit|yesno }}
    </template>
    <template v-slot:item.display_unit="{ item }">
      {{ item.display_unit|yesno }}
    </template>
    <template v-slot:item.unit_subsets="{ item }">
      {{ displayList(item.unit_subsets) }}
    </template>
    <template v-slot:item.ct_units="{ item }">
      {{ displayList(item.ct_units) }}
    </template>
    <template v-slot:item.convertible_unit="{ item }">
      {{ item.convertible_unit|yesno }}
    </template>
    <template v-slot:item.si_unit="{ item }">
      {{ item.si_unit|yesno }}
    </template>
    <template v-slot:item.us_conventional_unit="{ item }">
      {{ item.us_conventional_unit|yesno }}
    </template>
    <template v-slot:item.status="{ item }">
      <status-chip :status="item.status" />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date | date }}
    </template>
    <template v-slot:item.ucum_unit="{ item }">
      <v-edit-dialog
        :return-value.sync="item.ucum_unit"
        >
        <span v-if="item.ucum_unit">{{ item.ucum_unit.code }}</span>
        <v-icon v-else>mdi-table-search</v-icon>
        <template v-slot:input>
          <ucum-unit-field
            v-model="item.ucum_unit"
            />
        </template>
      </v-edit-dialog>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
  </n-n-table>
  <unit-form
    :open="showForm"
    @close="close()"
    :unit="activeUnit"/>
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import StatusChip from '@/components/tools/StatusChip'
import UnitForm from '@/components/library/UnitForm'
import ActionsMenu from '@/components/tools/ActionsMenu'
import StudybuilderUCUMField from '@/components/tools/StudybuilderUCUMField'
import units from '@/api/units'

export default {
  components: {
    NNTable,
    StatusChip,
    'ucum-unit-field': StudybuilderUCUMField,
    UnitForm,
    ActionsMenu
  },
  data () {
    return {
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('UnitTable.master_unit'), value: 'master_unit' },
        { text: this.$t('UnitTable.display_unit'), value: 'display_unit' },
        { text: this.$t('UnitTable.unit_subsets'), value: 'unit_subsets' },
        { text: this.$t('UnitTable.ucum_unit'), value: 'ucum.name' },
        { text: this.$t('UnitTable.ct_units'), value: 'ct_units', width: '10%' },
        { text: this.$t('UnitTable.convertible_unit'), value: 'convertible_unit' },
        { text: this.$t('UnitTable.si_unit'), value: 'si_unit' },
        { text: this.$t('UnitTable.us_conventional_unit'), value: 'us_conventional_unit' },
        { text: this.$t('UnitTable.unit_dimension'), value: 'unit_dimension.name' },
        { text: this.$t('UnitTable.legacy_code'), value: 'legacy_code' },
        { text: this.$t('UnitTable.molecular_weight'), value: 'molecular_weight_conv_expon' },
        { text: this.$t('UnitTable.conversion_factor'), value: 'conversion_factor_to_master' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ],
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.status === 'Draft',
          click: this.editUnit
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => (item.status === 'Draft' && parseFloat(item.version) < 1),
          click: this.deleteUnit
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) => item.status === 'Final',
          click: this.newUnitVersion
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) => item.status === 'Draft',
          click: this.approveUnit
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) => item.status === 'Final',
          click: this.inactivateUnit
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) => item.status === 'Retired',
          click: this.reactivateUnit
        }
      ],
      showForm: false,
      options: {},
      filters: '',
      total: 0,
      units: [],
      activeUnit: {}
    }
  },
  methods: {
    displayList (items) {
      return items.map(item => item.name).join(', ')
    },
    getUnits (filters, sort, filtersUpdated) {
      this.filters = filters
      let data
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      if (filtersUpdated) {
        /* Filters have changed, reset page number */
        this.options.page = 1
      }
      if (this.filters && this.filters !== undefined && filters !== '{}') {
        const filtersObj = JSON.parse(filters)
        if (Object.keys(filtersObj).length !== 0 && filtersObj.constructor === Object) {
          params.filters = JSON.stringify(filtersObj)
        }
      }
      if (this.options.sortBy.length !== 0 && sort !== undefined) {
        params.sort_by = `{"${this.options.sortBy[0]}":${!sort}}`
      } else {
        params.sort_by = `{"start_date":${false}}`
      }
      this.$store.dispatch('units/fetchUnits', { params }).then((resp) => {
        data = this.$store.getters['units/units']
        this.units = data.items
        this.total = data.total
      })
    },
    editUnit (item) {
      this.activeUnit = item
      this.showForm = true
    },
    deleteUnit (item) {
      units.delete(item.uid).then(resp => {
        this.getUnits()
      })
    },
    newUnitVersion (item) {
      units.newVersion(item.uid).then(resp => {
        this.getUnits()
      })
    },
    approveUnit (item) {
      units.approve(item.uid).then(resp => {
        this.getUnits()
      })
    },
    inactivateUnit (item) {
      units.inactivate(item.uid).then(resp => {
        this.getUnits()
      })
    },
    reactivateUnit (item) {
      units.reactivate(item.uid).then(resp => {
        this.getUnits()
      })
    },
    close () {
      this.showForm = false
      this.getUnits()
    }
  },
  watch: {
    options: {
      handler () {
        this.getUnits()
      },
      deep: true
    }
  }
}
</script>
