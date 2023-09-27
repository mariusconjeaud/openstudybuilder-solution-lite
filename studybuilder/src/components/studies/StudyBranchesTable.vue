<template>
<div>
  <n-n-table
    @filter="fetchStudyBranchArms"
    :headers="headers"
    item-key="branch_arm_uid"
    :server-items-length="total"
    :options.sync="options"
    :items="branchArms"
    :no-data-text="arms.length === 0 ? $t('StudyBranchArms.no_data') : undefined"
    :export-data-url="exportDataUrl"
    export-object-label="StudyBranches"
    :history-data-fetcher="fetchBranchArmsHistory"
    :history-title="$t('StudyBranchArms.global_history_title')"
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
        @click.stop="addBranchArm"
        :title="$t('StudyBranchArms.add_branch')"
        data-cy="add-study-branch-arm"
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
          <td width="7%">
            <v-icon
              small
              class="page__grab-icon">
              mdi-sort
            </v-icon>
            {{ item.order }}
          </td>
          <td width="15%">{{ item.arm_root.name }}</td>
          <td width="15%">{{ item.name }}</td>
          <td width="15%">{{ item.short_name }}</td>
          <td width="10%">{{ item.randomization_group }}</td>
          <td width="10%">{{ item.code }}</td>
          <td width="5%">{{ item.number_of_subjects }}</td>
          <td width="10%">{{ item.description }}</td>
          <td width="10%"><v-chip :color="item.colour_code" small /></td>
          <td width="10%">{{ item.start_date | date }}</td>
          <td width="10%">{{ item.user_initials }}</td>
        </tr>
      </draggable>
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
  <study-branches-form
    :open="showBranchArmsForm"
    @close="closeForm"
    :editedBranchArm="branchArmToEdit"
    :arms="arms"/>
  <v-dialog
    v-model="showBranchHistory"
    @keydown.esc="closeBranchHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="studyBranchHistoryTitle"
      @close="closeBranchHistory"
      :headers="headers"
      :items="branchHistoryItems"
      />
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import NNTable from '@/components/tools/NNTable'
import arms from '@/api/arms'
import StudyBranchesForm from '@/components/studies/StudyBranchesForm'
import { mapGetters } from 'vuex'
import ActionsMenu from '@/components/tools/ActionsMenu'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import { bus } from '@/main'
import draggable from 'vuedraggable'
import studyEpochs from '@/api/studyEpochs'
import { accessGuard } from '@/mixins/accessRoleVerifier'
import HistoryTable from '@/components/tools/HistoryTable'

export default {
  mixins: [accessGuard],
  components: {
    NNTable,
    StudyBranchesForm,
    ActionsMenu,
    ConfirmDialog,
    HistoryTable,
    draggable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-branch-arms`
    },
    studyBranchHistoryTitle () {
      if (this.selectedBranch) {
        return this.$t(
          'StudyBranchArms.study_branch_history_title',
          { branchUid: this.selectedBranch.branch_arm_uid })
      }
      return ''
    }
  },
  data () {
    return {
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyBranchArms.arm_name'), value: 'arm_root.name', historyHeader: 'arm_root_uid' },
        { text: this.$t('StudyBranchArms.name'), value: 'name' },
        { text: this.$t('StudyBranchArms.short_name'), value: 'short_name' },
        { text: this.$t('StudyBranchArms.randomisation_group'), value: 'randomization_group' },
        { text: this.$t('StudyBranchArms.code'), value: 'code' },
        { text: this.$t('StudyBranchArms.number_of_subjects'), value: 'number_of_subjects' },
        { text: this.$t('StudyBranchArms.description'), value: 'description' },
        { text: this.$t('StudyBranchArms.colour'), value: 'colour_code' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' }
      ],
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          click: this.editBranchArm,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          click: this.deleteBranchArm,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openBranchHistory
        }
      ],
      options: {},
      total: 0,
      arms: [],
      showBranchArmsForm: false,
      branchArmToEdit: {},
      branchArms: [],
      sortMode: false,
      showBranchHistory: false,
      branchHistoryItems: [],
      selectedBranch: null,
      showStudyBranchesHistory: false
    }
  },
  mounted () {
    this.fetchStudyArms()
  },
  methods: {
    async fetchBranchArmsHistory () {
      const resp = await studyEpochs.getStudyBranchesVersions(this.selectedStudy.uid)
      return resp.data
    },
    fetchStudyArms () {
      const params = {
        total_count: true,
        page_size: 0
      }
      arms.getAllForStudy(this.selectedStudy.uid, params).then(resp => {
        this.arms = resp.data.items
      })
    },
    fetchStudyBranchArms () {
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true
      }
      arms.getAllBranchArms(this.selectedStudy.uid, params).then(resp => {
        this.branchArms = resp.data
        this.total = resp.data.total
      })
    },
    closeForm () {
      this.branchArmToEdit = {}
      this.showBranchArmsForm = false
      this.fetchStudyBranchArms()
    },
    editBranchArm (item) {
      this.branchArmToEdit = item
      this.showBranchArmsForm = true
    },
    async openBranchHistory (branch) {
      this.selectedBranch = branch
      const resp = await studyEpochs.getStudyBranchVersions(this.selectedStudy.uid, branch.branch_arm_uid)
      this.branchHistoryItems = resp.data
      this.showBranchHistory = true
    },
    closeBranchHistory () {
      this.showBranchHistory = false
      this.selectedBranch = null
    },
    async deleteBranchArm (item) {
      let cellsInBranch = 0
      await arms.getAllCellsForBranch(this.selectedStudy.uid, item.branch_arm_uid).then(resp => {
        cellsInBranch = resp.data.length
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue')
      }
      if (cellsInBranch === 0) {
        arms.deleteBranchArm(this.selectedStudy.uid, item.branch_arm_uid).then(resp => {
          this.fetchStudyBranchArms()
          bus.$emit('notification', { msg: this.$t('StudyBranchArms.branch_deleted') })
        })
      } else if (await this.$refs.confirm.open(this.$t('StudyBranchArms.branch_delete_notification'), options)) {
        arms.deleteBranchArm(this.selectedStudy.uid, item.branch_arm_uid).then(resp => {
          this.fetchStudyBranchArms()
          bus.$emit('notification', { msg: this.$t('StudyBranchArms.branch_deleted') })
        })
      }
    },
    async addBranchArm () {
      this.fetchStudyArms()
      if (this.arms.length === 0) {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('StudyBranchArms.add_arm'),
          redirect: 'arms'
        }
        if (!await this.$refs.confirm.open(this.$t('StudyBranchArms.add_arm_message'), options)) {
          return
        }
      }
      this.showBranchArmsForm = true
    },
    onChange (event) {
      const branch = event.moved.element
      const newOrder = {
        new_order: this.branchArms[event.moved.newIndex].order
      }
      arms.updateBranchArmOrder(this.selectedStudy.uid, branch.branch_arm_uid, newOrder).then(resp => {
        this.fetchStudyBranchArms()
      })
    }
  },
  watch: {
    options () {
      this.fetchStudyBranchArms()
    }
  }
}
</script>
