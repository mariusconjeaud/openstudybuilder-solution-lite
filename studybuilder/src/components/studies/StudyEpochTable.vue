<template>
<div>
  <n-n-table
    :headers="headers"
    :defaultHeaders="headers"
    :items="studyEpochs"
    item-key="uid"
    :options.sync="options"
    :export-data-url="exportDataUrl"
    export-object-label="StudyEpochs"
    @filter="fetchEpochs"
    has-api
    :column-data-resource="`studies/${selectedStudy.uid}/study-epochs`"
    :history-data-fetcher="fetchEpochsHistory"
    :history-title="$t('StudyEpochTable.global_history_title')"
    >
    <template v-slot:item.color_hash="{ item }">
      <v-chip :data-cy="'color='+item.color_hash" :color="item.color_hash" small />
    </template>
    <template v-slot:afterSwitches>
      <div :title="$t('NNTableTooltips.reorder_content')">
        <v-switch
          v-model="sortMode"
          :label="$t('NNTable.reorder_content')"
          hide-details
          class="mr-6"
          @change="switchSort"
          />
      </div>
    </template>
    <template v-slot:body="props" v-if="sortMode">
      <draggable
        :list="props.items"
        tag="tbody"
        @change="onOrderChange($event)"
        >
        <tr
          v-for="(item, index) in props.items"
          :key="index"
          >
          <td v-if="props.showSelectBoxes">
            <v-checkbox
              :value="item.uid"
              hide-details
              @change="props.select(!props.isSelected(item))"
              />
          </td>
          <td>
            <actions-menu :actions="actions" :item="item" />
          </td>
          <td></td>
          <td>
            <v-icon
              small
              class="page__grab-icon"
              >
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td>{{ item.epoch_name }}</td>
          <td>{{ getDisplay(item, 'epoch_type') }}</td>
          <td>{{ getDisplay(item, 'epoch_subtype') }}</td>
          <td>{{ item.start_rule }}</td>
          <td>{{ item.end_rule }}</td>
          <td>{{ item.description }}</td>
          <td>{{ item.study_visit_count }}</td>
          <td><v-chip :data-cy="'color='+item.color_hash" :color="item.color_hash" small /></td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.epoch_type="{ item }">{{ getDisplay(item, 'epoch_type') }}</template>
    <template v-slot:item.epoch_subtype="{ item }">{{ getDisplay(item, 'epoch_subtype') }}</template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:actions="">
      <v-btn
        data-cy="create-epoch"
        fab
        dark
        small
        color="primary"
        @click="createEpoch()"
        :title="$t('StudyEpochForm.add_title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <study-epoch-form
    :open="showForm"
    :studyEpoch="selectedStudyEpoch"
    @close="closeForm"
    />
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import ActionsMenu from '@/components/tools/ActionsMenu'
import NNTable from '@/components/tools/NNTable'
import StudyEpochForm from './StudyEpochForm'
import terms from '@/api/controlledTerminology/terms'
import { bus } from '@/main'
import epochs from '@/api/studyEpochs'
import draggable from 'vuedraggable'
import filteringParameters from '@/utils/filteringParameters'

export default {
  components: {
    ActionsMenu,
    NNTable,
    StudyEpochForm,
    draggable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyEpochs: 'studyEpochs/studyEpochs'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-epochs`
    },
    studyEpochHistoryTitle () {
      if (this.selectedStudyEpoch) {
        return this.$t(
          'StudyEpochTable.study_epoch_history_title',
          { epochUid: this.selectedStudyEpoch.uid })
      }
      return ''
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          condition: (item) => item.possible_actions.find(action => action === 'edit'),
          click: this.editEpoch
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          condition: (item) => item.possible_actions.find(action => action === 'delete'),
          click: this.deleteEpoch
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openEpochHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyEpochTable.number'), value: 'order', width: '5%' },
        { text: this.$t('StudyEpochTable.name'), value: 'epoch_name' },
        { text: this.$t('StudyEpochTable.type'), value: 'epoch_type' },
        { text: this.$t('StudyEpochTable.sub_type'), value: 'epoch_subtype' },
        { text: this.$t('StudyEpochTable.start_rule'), value: 'start_rule' },
        { text: this.$t('StudyEpochTable.end_rule'), value: 'end_rule' },
        { text: this.$t('StudyEpochTable.description'), value: 'description', width: '20%' },
        { text: this.$t('StudyEpochTable.visit_count'), value: 'study_visit_count' },
        { text: this.$t('StudyEpochTable.colour'), value: 'color_hash' }
      ],
      defaultColums: [
        { text: '', value: 'actions', width: '5%' },
        { text: this.$t('StudyEpochTable.number'), value: 'order', width: '3%' },
        { text: this.$t('StudyEpochTable.name'), value: 'epoch_name' },
        { text: this.$t('StudyEpochTable.sub_type'), value: 'epoch_subtype' },
        { text: this.$t('StudyEpochTable.type'), value: 'epoch_type' },
        { text: this.$t('StudyEpochTable.start_rule'), value: 'start_rule' },
        { text: this.$t('StudyEpochTable.end_rule'), value: 'end_rule' },
        { text: this.$t('StudyEpochTable.description'), value: 'description' }
      ],
      selectedStudyEpoch: null,
      showForm: false,
      showEpochHistory: false,
      epochHistoryItems: [],
      componentKey: 0,
      calculatedItems: {},
      showStudyEpochsHistory: false,
      sortMode: false,
      selectMode: false,
      options: {},
      total: 0
    }
  },
  methods: {
    async fetchEpochsHistory () {
      const resp = await epochs.getStudyEpochsVersions(this.selectedStudy.uid)
      return this.transformItems(resp.data)
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.epoch_type) {
          newItem.epoch_type = this.getDisplay(newItem, 'epoch_type')
        }
        if (newItem.epoch_subtype) {
          newItem.epoch_subtype = this.getDisplay(newItem, 'epoch_subtype')
        }
        result.push(newItem)
      }
      return result
    },
    fetchEpochs (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.studyUid = this.selectedStudy.uid
      this.$store.dispatch('studyEpochs/fetchFilteredStudyEpochs', params)
    },
    switchSort () {
      if (this.selectMode && this.sortMode) {
        this.selectMode = false
      } else if (this.sortMode) {
        this.headers.unshift({ text: '', value: 'order', sortable: false, width: '5px' })
      } else {
        this.headers.shift()
      }
    },
    switchSelect () {
      if (this.sortMode && this.selectMode) {
        this.sortMode = false
      }
    },
    getDisplay (item, name) {
      if (name in this.calculatedItems) {
        return this.calculatedItems[name][item[name]]
      } else {
        return item[name]
      }
    },
    createMapping (codelist) {
      const returnValue = {}
      codelist.forEach(item => {
        returnValue[item.term_uid] = item.sponsor_preferred_name
      })
      return returnValue
    },
    editEpoch (item) {
      this.selectedStudyEpoch = item
      this.showForm = true
    },
    onOrderChange (event) {
      epochs.reorderStudyEpoch(this.selectedStudy.uid, this.studyEpochs[event.moved.oldIndex].uid, event.moved.newIndex).then(item => {
        this.$store.dispatch('studyEpochs/fetchStudyEpochs', this.selectedStudy.uid)
      })
    },
    createEpoch () {
      this.selectedStudyEpoch = null
      this.showForm = true
    },
    closeForm () {
      this.selectedStudyEpoch = null
      this.showForm = false
    },
    deleteEpoch (item) {
      if (item.study_visit_count > 0) {
        const epoch = item.epoch_name
        bus.$emit('notification', { type: 'warning', msg: this.$t('StudyEpochTable.epoch_linked_to_visits_warning', { epoch }) })
        return
      }
      this.$store.dispatch('studyEpochs/deleteStudyEpoch', { studyUid: this.selectedStudy.uid, studyEpochUid: item.uid }).then(resp => {
        bus.$emit('notification', { msg: this.$t('StudyEpochTable.delete_success') })
      })
    },
    async openEpochHistory (epoch) {
      this.selectedStudyEpoch = epoch
      const resp = await epochs.getStudyEpochVersions(this.selectedStudy.uid, epoch.uid)
      this.epochHistoryItems = this.transformItems(resp.data)
      this.showEpochHistory = true
    },
    closeEpochHistory () {
      this.selectedStudyEpoch = null
      this.showEpochHistory = false
    }
  },
  mounted () {
    terms.getByCodelist('epochs').then(resp => {
      this.$set(this.calculatedItems, 'epoch', this.createMapping(resp.data.items))
    })
    terms.getByCodelist('epochTypes').then(resp => {
      this.$set(this.calculatedItems, 'epoch_type', this.createMapping(resp.data.items))
    })
    terms.getByCodelist('epochSubTypes').then(resp => {
      this.$set(this.calculatedItems, 'epoch_subtype', this.createMapping(resp.data.items))
    })
    this.$store.dispatch('studyEpochs/fetchStudyEpochs', this.selectedStudy.uid)
    this.$store.dispatch('studiesGeneral/fetchUnits')
    this.fetchEpochs()
  }
}
</script>
