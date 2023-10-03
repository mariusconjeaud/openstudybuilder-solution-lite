<template>
<div>
  <n-n-table
    @filter="fetchStudyCohorts"
    :headers="headers"
    item-key="cohort_uid"
    :server-items-length="total"
    :options.sync="options"
    :items="cohorts"
    :history-data-fetcher="fetchCohortsHistory"
    :history-title="$t('StudyCohorts.global_history_title')"
    :export-data-url="exportDataUrl"
    export-object-label="StudyCohors"
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
        fab
        small
        color="primary"
        @click.stop="showForm()"
        :title="$t('StudyCohorts.add_study_cohort')"
        data-cy="add-study-cohort"
        :disabled="!checkPermission($roles.STUDY_WRITE)"
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
          <td width="3%">
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
          <td width="10%">{{ item.arm_roots|names }}</td>
          <td width="10%">{{ item.branch_arm_roots|names }}</td>
          <td width="10%">{{ item.name }}</td>
          <td width="10%">{{ item.short_name }}</td>
          <td width="10%">{{ item.code }}</td>
          <td width="5%">{{ item.number_of_subjects }}</td>
          <td width="10%">{{ item.description }}</td>
          <td width="10%"><v-chip :color="item.colour_code" small /></td>
          <td width="10%">{{ item.start_date | date }}</td>
          <td width="10%">{{ item.user_initials }}</td>
        </tr>
      </draggable>
    </template>
    <template v-slot:item.arm_roots="{ item }">
      {{ item.arm_roots|names }}
    </template>
    <template v-slot:item.branch_arm_roots="{ item }">
      {{ (item.branch_arm_roots !== null)?item.branch_arm_roots:[]|names }}
    </template>
    <template v-slot:item.colour_code="{ item }">
      <v-chip :data-cy="'color='+item.colour_code" :color="item.colour_code" small />
    </template>
    <template v-slot:item.start_date="{ item }">
      {{ item.start_date|date }}
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
  </n-n-table>
  <study-cohorts-form
    :open="form"
    @close="closeForm"
    :editedCohort="cohortToEdit"
    :arms="arms"
    :branches="branches"/>
  <v-dialog
    v-model="showCohortHistory"
    @keydown.esc="closeCohortHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="studyCohortHistoryTitle"
      @close="closeCohortHistory"
      :headers="headers"
      :items="cohortHistoryItems"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>

import NNTable from '@/components/tools/NNTable'
import arms from '@/api/arms'
import StudyCohortsForm from '@/components/studies/StudyCohortsForm'
import { mapGetters } from 'vuex'
import ActionsMenu from '@/components/tools/ActionsMenu'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import { bus } from '@/main'
import draggable from 'vuedraggable'
import { accessGuard } from '@/mixins/accessRoleVerifier'
import HistoryTable from '@/components/tools/HistoryTable'

export default {
  mixins: [accessGuard],
  components: {
    NNTable,
    StudyCohortsForm,
    ActionsMenu,
    ConfirmDialog,
    HistoryTable,
    draggable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    studyCohortHistoryTitle () {
      if (this.selectedCohort) {
        return this.$t(
          'StudyCohorts.study_arm_history_title',
          { cohortUid: this.selectedCohort.cohort_uid })
      }
      return ''
    },
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-cohorts`
    }
  },
  data () {
    return {
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyCohorts.arm_name'), value: 'arm_roots', historyHeader: 'arm_roots_uids' },
        { text: this.$t('StudyCohorts.branch_arm_name'), value: 'branch_arm_roots', historyHeader: 'branch_arm_roots_uids' },
        { text: this.$t('StudyCohorts.cohort_name'), value: 'name' },
        { text: this.$t('StudyCohorts.cohort_short_name'), value: 'short_name' },
        { text: this.$t('StudyCohorts.cohort_code'), value: 'code' },
        { text: this.$t('StudyCohorts.number_of_subjects'), value: 'number_of_subjects' },
        { text: this.$t('_global.description'), value: 'description' },
        { text: this.$t('StudyCohorts.colour'), value: 'colour_code' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          click: this.editCohort,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          click: this.deleteCohort,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openCohortHistory
        }
      ],
      options: {},
      total: 0,
      cohorts: [],
      form: false,
      sortMode: false,
      arms: [],
      branches: [],
      cohortToEdit: {},
      showCohortHistory: false,
      cohortHistoryItems: [],
      selectedCohort: null,
      showStudyCohortsHistory: false
    }
  },
  mounted () {
    this.fetchStudyCohorts()
    this.fetchStudyArmsAndBranches()
  },
  methods: {
    async fetchCohortsHistory () {
      const resp = await arms.getStudyCohortsVersions(this.selectedStudy.uid)
      return resp.data
    },
    fetchStudyArmsAndBranches () {
      const params = {
        total_count: true,
        page_size: 0
      }
      arms.getAllForStudy(this.selectedStudy.uid, params).then(resp => {
        this.arms = resp.data.items
      })
      arms.getAllBranchArms(this.selectedStudy.uid, params).then(resp => {
        this.branches = resp.data
      })
    },
    fetchStudyCohorts () {
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      arms.getAllCohorts(this.selectedStudy.uid, params).then(resp => {
        this.cohorts = resp.data.items
        this.total = resp.data.total
      })
    },
    showForm () {
      this.form = true
    },
    closeForm () {
      this.form = false
      this.cohortToEdit = {}
      this.fetchStudyCohorts()
    },
    editCohort (item) {
      this.cohortToEdit = item
      this.form = true
    },
    async openCohortHistory (cohort) {
      this.selectedCohort = cohort
      const resp = await arms.getStudyCohortVersions(this.selectedStudy.uid, cohort.cohort_uid)
      this.cohortHistoryItems = resp.data
      this.showCohortHistory = true
    },
    closeCohortHistory () {
      this.showCohortHistory = false
      this.selectedCohort = null
    },
    deleteCohort (item) {
      arms.deleteCohort(this.selectedStudy.uid, item.cohort_uid).then(resp => {
        this.fetchStudyCohorts()
        bus.$emit('notification', { msg: this.$t('StudyCohorts.cohort_deleted') })
      })
    },
    onChange (event) {
      const cohort = event.moved.element
      const newOrder = {
        new_order: this.cohorts[event.moved.newIndex].order
      }
      arms.updateCohortOrder(this.selectedStudy.uid, cohort.cohort_uid, newOrder).then(resp => {
        this.fetchStudyCohorts()
      })
    }
  },
  watch: {
    options () {
      this.fetchStudyCohorts()
    }
  }
}
</script>
