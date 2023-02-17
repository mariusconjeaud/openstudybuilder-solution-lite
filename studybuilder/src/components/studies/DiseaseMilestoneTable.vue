<template>
<div>
  <n-n-table
    :headers="headers"
    :items="diseaseMilestones"
    item-key="uid"
    fixed-header
    :options.sync="options"
    :server-items-length="total"
    :history-data-fetcher="fetchDiseaseMilestonesHistory"
    :history-title="$t('DiseaseMilestoneTable.global_history_title')"
    @filter="fetchDiseaseMilestones"
    export-object-label="DiseaseMilestones"
    :export-data-url="exportDataUrl"
    :column-data-resource="exportDataUrl"
    has-api
    >
    <template v-slot:afterSwitches>
      <div :title="$t('NNTableTooltips.reorder_content')">
        <v-switch
          v-model="sortMode"
          :label="$t('NNTable.reorder_content')"
          hide-details
          class="mr-6"
          />
      </div>
    </template>
    <template v-slot:actions="">
      <v-btn
        data-cy="create-disease-milestone"
        fab
        dark
        small
        color="primary"
        @click="createDiseaseMilestone()"
        :title="$t('DiseaseMilestoneForm.add_title')"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:body="props" v-if="sortMode">
      <draggable
        :list="props.items"
        tag="tbody"
        @change="onChange($event)"
        >
        <tr
          v-for="(item, index) in props.items"
          :key="index"
          >
          <td width="5%">
            <actions-menu :actions="actions" :item="item"/>
          </td>
          <td width="5%">
            <v-icon
              small
              class="page__grab-icon">
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td>{{ item.disease_milestone_type_named }}</td>
          <td>{{ item.disease_milestone_type_definition }}</td>
          <td>{{ item.repetition_indicator|yesno }}</td>
          <td>{{ item.start_date | date }}</td>
          <td>{{ item.user_initials }}</td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.actions="{ item }">
      <div class="pr-0 mr-0">
        <actions-menu :actions="actions" :item="item"/>
      </div>
    </template>
    <template v-slot:item.repetition_indicator="{ item }">
      {{ item.repetition_indicator|yesno }}
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date|date }}
    </template>
  </n-n-table>
  <disease-milestone-form
    :open="showForm"
    :disease-milestone="selectedDiseaseMilestone"
    @close="closeForm"
    />
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
  <v-dialog
    v-model="showHistory"
    @keydown.esc="closeHistory"
    persistent
    max-width="1200px"
    >
    <history-table
      :title="diseaseMilestoneHistoryTitle"
      @close="closeHistory"
      :headers="headers"
      :items="historyItems"
      />
  </v-dialog>
</div>
</template>

<script>
import ActionsMenu from '@/components/tools/ActionsMenu'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import dataFormating from '@/utils/dataFormating'
import DiseaseMilestoneForm from './DiseaseMilestoneForm'
import draggable from 'vuedraggable'
import filteringParameters from '@/utils/filteringParameters'
import HistoryTable from '@/components/tools/HistoryTable'
import { mapGetters } from 'vuex'
import NNTable from '@/components/tools/NNTable'
import study from '@/api/study'

export default {
  components: {
    ActionsMenu,
    ConfirmDialog,
    DiseaseMilestoneForm,
    draggable,
    HistoryTable,
    NNTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-disease-milestones`
    },
    diseaseMilestoneHistoryTitle () {
      if (this.selectedDiseaseMilestone) {
        return this.$t(
          'DiseaseMilestoneTable.item_history_title',
          { uid: this.selectedDiseaseMilestone.uid })
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
          click: this.editDiseaseMilestone
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteDiseaseMilestone
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openHistory
        }
      ],
      diseaseMilestones: [],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('DiseaseMilestone.disease_milestone_type'), value: 'disease_milestone_type_named' },
        { text: this.$t('_global.definition'), value: 'disease_milestone_type_definition' },
        { text: this.$t('DiseaseMilestone.repetition_indicator'), value: 'repetition_indicator' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      historyItems: [],
      options: {},
      selectedDiseaseMilestone: null,
      showForm: false,
      showHistory: false,
      sortMode: false,
      total: 0
    }
  },
  methods: {
    fetchDiseaseMilestones (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      study.getStudyDiseaseMilestones(this.selectedStudy.uid, params).then(resp => {
        this.diseaseMilestones = resp.data.items
        this.total = resp.data.total
      })
    },
    formatItems (items) {
      const result = []
      for (const item of items) {
        item.repetition_indicator = dataFormating.yesno(item.repetition_indicator)
        result.push(item)
      }
      return result
    },
    async fetchDiseaseMilestonesHistory () {
      const resp = await study.getStudyDiseaseMilestonesAuditTrail(this.selectedStudy.uid)
      return this.formatItems(resp.data)
    },
    createDiseaseMilestone () {
      this.selectedDiseaseMilestone = null
      this.showForm = true
    },
    closeForm () {
      this.showForm = false
      this.fetchDiseaseMilestones()
    },
    editDiseaseMilestone (item) {
      this.selectedDiseaseMilestone = item
      this.showForm = true
    },
    async deleteDiseaseMilestone (item) {
      const options = { type: 'warning' }
      const context = { name: item.disease_milestone_type_named }
      const msg = this.$t('DiseaseMilestoneTable.confirm_delete', context)
      if (!await this.$refs.confirm.open(msg, options)) {
        return
      }
      study.deleteStudyDiseaseMilestone(this.selectedStudy.uid, item.uid).then(resp => {
        bus.$emit('notification', { msg: this.$t('DiseaseMilestoneTable.delete_success') })
        this.fetchDiseaseMilestones()
      })
    },
    async openHistory (item) {
      this.selectedDiseaseMilestone = item
      const resp = await study.getStudyDiseaseMilestoneAuditTrail(this.selectedStudy.uid, item.uid)
      this.historyItems = this.formatItems(resp.data)
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
    },
    onChange (event) {
      const diseaseMilestone = event.moved.element
      const newOrder = {
        new_order: this.diseaseMilestones[event.moved.newIndex].order
      }
      study.updateStudyDiseaseMilestoneOrder(this.selectedStudy.uid, diseaseMilestone.uid, newOrder).then(resp => {
        this.fetchDiseaseMilestones()
      })
    }
  },
  mounted () {
    this.fetchDiseaseMilestones()
  }
}
</script>
