<template>
<div>
  <n-n-table
    @filter="fetchStudyArms"
    :headers="headers"
    item-key="arm_uid"
    :server-items-length="total"
    :options.sync="options"
    :export-data-url="exportDataUrl"
    export-object-label="StudyArms"
    :items="arms"
    has-api
    :column-data-resource="`studies/${selectedStudy.uid}/study-arms`"
    :history-data-fetcher="fetchArmsHistory"
    :history-title="$t('StudyArmsTable.global_history_title')"
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
          <td width="3%">
            <actions-menu :actions="actions" :item="item"/>
          </td>
          <td width="7%">
            <v-icon
              small
              class="page__grab-icon">
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td width="10%">{{ item.arm_type.sponsor_preferred_name }}</td>
          <td width="10%">{{ item.name }}</td>
          <td width="10%">{{ item.short_name }}</td>
          <td width="10%">{{ item.randomization_group }}</td>
          <td width="5%">{{ item.code }}</td>
          <td width="5%">{{ item.number_of_subjects }}</td>
          <td width="10%">{{ item.description }}</td>
          <td width="10%"><v-chip :color="item.arm_colour" small /></td>
          <td width="15%">{{ item.start_date | date }}</td>
          <td width="10%">{{ item.user_initials }}</td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date|date }}
    </template>
    <template v-slot:item.arm_connected_branch_arms="{ item }">
      <template v-if="item.arm_connected_branch_arms">
        {{ item.arm_connected_branch_arms|names }}
      </template>
    </template>
    <template v-slot:item.arm_colour="{ item }">
      <v-chip :color="item.arm_colour" small />
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:actions="">
      <v-btn
        fab
        dark
        small
        color="primary"
        @click.stop="showArmsForm = true"
        :title="$t('StudyArmsForm.add_arm')"
        data-cy="add-study-arm"
        >
        <v-icon dark>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <study-arms-form
    :open="showArmsForm"
    @close="closeForm"
    :editedArm="armToEdit"
    />
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>

import NNTable from '@/components/tools/NNTable'
import arms from '@/api/arms'
import StudyArmsForm from '@/components/studies/StudyArmsForm'
import { mapGetters } from 'vuex'
import ActionsMenu from '@/components/tools/ActionsMenu'
import { bus } from '@/main'
import draggable from 'vuedraggable'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import filteringParameters from '@/utils/filteringParameters'
import studyEpochs from '@/api/studyEpochs'

export default {
  components: {
    NNTable,
    StudyArmsForm,
    ActionsMenu,
    draggable,
    ConfirmDialog
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-arms`
    },
    studyArmHistoryTitle () {
      if (this.selectedArm) {
        return this.$t(
          'StudyArmsTable.study_arm_history_title',
          { armUid: this.selectedArm.arm_uid })
      }
      return ''
    }
  },
  data () {
    return {
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyArmsTable.type'), value: 'arm_type.sponsor_preferred_name', width: '7%' },
        { text: this.$t('StudyArmsTable.name'), value: 'name' },
        { text: this.$t('StudyArmsTable.short_name'), value: 'short_name' },
        { text: this.$t('StudyArmsTable.randomisation_group'), value: 'randomization_group' },
        { text: this.$t('StudyArmsTable.code'), value: 'code' },
        { text: this.$t('StudyArmsTable.number_of_subjects'), value: 'number_of_subjects', width: '1%' },
        { text: this.$t('StudyArmsTable.connected_branches'), value: 'arm_connected_branch_arms' },
        { text: this.$t('StudyArmsTable.description'), value: 'description' },
        { text: this.$t('StudyBranchArms.colour'), value: 'arm_colour' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil',
          iconColor: 'primary',
          click: this.editArm
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteArm
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openArmHistory
        }
      ],
      options: {},
      total: 0,
      arms: [],
      showArmsForm: false,
      armToEdit: {},
      sortMode: false,
      showArmHistory: false,
      armHistoryItems: [],
      selectedArm: null,
      showStudyArmsHistory: false
    }
  },
  methods: {
    async fetchArmsHistory () {
      const resp = await studyEpochs.getStudyArmsVersions(this.selectedStudy.uid)
      return resp.data
    },
    fetchStudyArms (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.studyUid = this.selectedStudy.uid
      arms.getAllForStudy(this.selectedStudy.uid, params).then(resp => {
        this.arms = resp.data.items
        this.total = resp.data.total
      })
    },
    closeForm () {
      this.armToEdit = {}
      this.showArmsForm = false
      this.fetchStudyArms()
    },
    editArm (item) {
      this.armToEdit = item
      this.showArmsForm = true
    },
    async openArmHistory (arm) {
      this.selectedArm = arm
      const resp = await studyEpochs.getStudyArmVersions(this.selectedStudy.uid, arm.arm_uid)
      this.armHistoryItems = resp.data
      this.showArmHistory = true
    },
    closeArmHistory () {
      this.showArmHistory = false
      this.selectedArm = null
    },
    async deleteArm (item) {
      let relatedItems = 0
      await arms.getAllBranchesForArm(this.selectedStudy.uid, item.arm_uid).then(resp => {
        relatedItems += resp.data.length
      })
      await arms.getAllCohortsForArm(this.selectedStudy.uid, item.arm_uid).then(resp => {
        relatedItems += resp.data.items.length
      })
      await arms.getAllCellsForArm(this.selectedStudy.uid, item.arm_uid).then(resp => {
        relatedItems += resp.data.length
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (relatedItems === 0) {
        arms.delete(this.selectedStudy.uid, item.arm_uid).then(resp => {
          bus.$emit('notification', { msg: this.$t('StudyArmsTable.arm_deleted') })
          this.fetchStudyArms()
        })
      } else if (await this.$refs.confirm.open(this.$t('StudyArmsTable.arm_delete_notification'), options)) {
        arms.delete(this.selectedStudy.uid, item.arm_uid).then(resp => {
          bus.$emit('notification', { msg: this.$t('StudyArmsTable.arm_deleted') })
          this.fetchStudyArms()
        })
      }
    },
    onChange (event) {
      const arm = event.moved.element
      const newOrder = {
        new_order: this.arms[event.moved.newIndex].order
      }
      arms.updateArmOrder(this.selectedStudy.uid, arm.arm_uid, newOrder).then(resp => {
        this.fetchStudyArms()
      })
    }
  },
  watch: {
    options () {
      this.fetchStudyArms()
    }
  }
}
</script>
