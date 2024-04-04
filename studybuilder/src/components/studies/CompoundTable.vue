<template>
<div>
  <n-n-table
    :headers="headers"
    :items="formatedStudyCompounds"
    item-key="study_compound_uid"
    export-object-label="StudyCompounds"
    :export-data-url="exportDataUrl"
    :column-data-resource="`studies/${selectedStudy.uid}/study-compounds`"
    has-api
    :options.sync="options"
    :server-items-length="total"
    @filter="fetchCompounds"
    :history-data-fetcher="fetchCompoundsHistory"
    :history-title="$t('StudyCompoundTable.global_history_title')"
    >
    <template v-slot:actions="">
      <v-btn
        data-cy="add-study-compound"
        fab
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('StudyCompoundForm.add_title')"
        :disabled="!checkPermission($roles.STUDY_WRITE) || selectedStudyVersion !== null"
        >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
    <template v-slot:item.compound.name="{ item }">
      <router-link :to="{ name: 'StudyCompoundOverview', params: { study_id: selectedStudy.uid, id: item.study_compound_uid } }">
        {{ item.compound.name }}
      </router-link>
    </template>
  </n-n-table>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
  <v-dialog
    v-model="showForm"
    persistent
    fullscreen
    content-class="fullscreen-dialog"
    >
    <compound-form
      @close="closeForm"
      :study-compound="selectedStudyCompound"
      />
  </v-dialog>
  <v-dialog
    v-model="showCompoundHistory"
    @keydown.esc="closeStudyCompoundHistory"
    persistent
    :max-width="globalHistoryDialogMaxWidth"
    :fullscreen="globalHistoryDialogFullscreen"
    >
    <history-table
      :title="studyCompoundHistoryTitle"
      @close="closeStudyCompoundHistory"
      :headers="headers"
      :items="compoundHistoryItems"
      />
  </v-dialog>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CompoundForm from './CompoundForm'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import dataFormating from '@/utils/dataFormating'
import HistoryTable from '@/components/tools/HistoryTable'
import filteringParameters from '@/utils/filteringParameters'
import NNTable from '@/components/tools/NNTable'
import study from '@/api/study'
import { accessGuard } from '@/mixins/accessRoleVerifier'

export default {
  mixins: [accessGuard],
  components: {
    ActionsMenu,
    CompoundForm,
    ConfirmDialog,
    HistoryTable,
    NNTable
  },
  computed: {
    ...mapGetters({
      nullValues: 'studiesGeneral/nullValues',
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion',
      studyCompounds: 'studyCompounds/studyCompounds'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-compounds`
    },
    studyCompoundHistoryTitle () {
      if (this.selectedStudyCompound) {
        return this.$t(
          'StudyCompoundTable.study_compound_history_title',
          { studyCompoundUid: this.selectedStudyCompound.study_compound_uid })
      }
      return ''
    },
    formatedStudyCompounds () {
      return this.transformItems(this.studyCompounds)
    }
  },
  data () {
    return {
      actions: [
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: () => !this.selectedStudyVersion,
          click: this.editStudyCompound,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: () => !this.selectedStudyVersion,
          click: this.deleteStudyCompound,
          accessRole: this.$roles.STUDY_WRITE
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openStudyCompoundHistory
        }
      ],
      compoundHistoryItems: [],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order' },
        { text: this.$t('StudyCompoundTable.type_of_treatment'), value: 'type_of_treatment.name' },
        { text: this.$t('StudyCompoundTable.reason_for_missing'), value: 'reason_for_missing_null_value.name' },
        { text: this.$t('StudyCompoundTable.compound'), value: 'compound.name' },
        { text: this.$t('StudyCompoundTable.sponsor_compound'), value: 'compound.is_sponsor_compound' },
        { text: this.$t('StudyCompoundTable.is_name_inn'), value: 'compound.is_name_inn' },
        { text: this.$t('StudyCompoundTable.substance'), value: 'substances' },
        { text: this.$t('StudyCompoundTable.pharma_class'), value: 'pharmacological_classes' },
        { text: this.$t('StudyCompoundTable.compound_alias'), value: 'compound_alias.name' },
        { text: this.$t('StudyCompoundTable.preferred_alias'), value: 'compound_alias.is_preferred_synonym' },
        { text: this.$t('StudyCompoundTable.strength'), value: 'strength_value' },
        { text: this.$t('StudyCompoundTable.dosage_form'), value: 'dosage_form.name' },
        { text: this.$t('StudyCompoundTable.route_of_admin'), value: 'route_of_administration.name' },
        { text: this.$t('StudyCompoundTable.dispensed_in'), value: 'dispensed_in.name' },
        { text: this.$t('StudyCompoundTable.device'), value: 'device.name' },
        { text: this.$t('StudyCompoundTable.half_life'), value: 'compound.half_life' },
        { text: this.$t('StudyCompoundTable.lag_time'), value: 'lag_times' },
        { text: this.$t('StudyCompoundTable.nnc_number_long'), value: 'nnc_long_number' },
        { text: this.$t('StudyCompoundTable.nnc_number_short'), value: 'nnc_short_number' },
        { text: this.$t('StudyCompoundTable.analyte_number'), value: 'analyte_number' },
        { text: this.$t('StudyCompoundTable.compound_definition'), value: 'compound.definition' },
        { text: this.$t('StudyCompoundTable.alias_definition'), value: 'compound_alias.definition' }
      ],
      selectedStudyCompound: null,
      showCompoundHistory: false,
      showForm: false,
      total: 0,
      options: {}
    }
  },
  methods: {
    fetchCompounds (filters, sort, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      params.studyUid = this.selectedStudy.uid
      params.study_value_version = this.selectedStudyVersion
      this.$store.dispatch('studyCompounds/fetchStudyCompounds', params).then(resp => {
        this.total = resp.data.total
      })
    },
    async fetchCompoundsHistory () {
      const resp = await study.getStudyCompoundsAuditTrail(this.selectedStudy.uid)
      return this.transformItems(resp.data)
    },
    async deleteStudyCompound (studyCompound) {
      const options = { type: 'warning' }
      let msg
      if (studyCompound.compound) {
        const compound = studyCompound.compound.name
        const context = { compound }
        if (studyCompound.study_compound_dosing_count) {
          context.compoundDosings = studyCompound.study_compound_dosing_count
          msg = this.$t('StudyCompoundTable.confirm_delete_cascade', context)
        } else {
          msg = this.$t('StudyCompoundTable.confirm_delete', context)
        }
      } else {
        msg = this.$t('StudyCompoundTable.confirm_delete_na')
      }
      if (!await this.$refs.confirm.open(msg, options)) {
        return
      }
      this.$store.dispatch('studyCompounds/deleteStudyCompound', {
        studyUid: this.selectedStudy.uid,
        studyCompoundUid: studyCompound.study_compound_uid
      }).then(resp => {
        bus.$emit('notification', { msg: this.$t('StudyCompoundTable.delete_compound_success') })
      })
    },
    editStudyCompound (studyCompound) {
      const originalItem = this.studyCompounds.find(item => item.study_compound_uid === studyCompound.study_compound_uid)
      this.selectedStudyCompound = originalItem
      this.showForm = true
    },
    async openStudyCompoundHistory (studyCompound) {
      this.selectedStudyCompound = studyCompound
      const resp = await study.getStudyCompoundAuditTrail(this.selectedStudy.uid, studyCompound.study_compound_uid)
      this.compoundHistoryItems = this.transformItems(resp.data)
      this.showCompoundHistory = true
    },
    closeStudyCompoundHistory () {
      this.selectedStudyCompound = null
      this.showCompoundHistory = false
    },
    closeForm () {
      this.showForm = false
      this.selectedStudyCompound = null
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.compound) {
          newItem.compound.is_sponsor_compound = dataFormating.yesno(newItem.compound.is_sponsor_compound)
          newItem.compound.is_name_inn = dataFormating.yesno(newItem.compound.is_name_inn)
          newItem.substances = dataFormating.substances(newItem.compound.substances)
          newItem.pharmacological_classes = dataFormating.pharmacologicalClasses(newItem.compound.substances)
          if (newItem.compound.half_life) {
            newItem.compound.half_life = dataFormating.numericValue(newItem.compound.half_life)
          }
          if (newItem.compound.lag_times) {
            newItem.lag_times = dataFormating.lagTimes(newItem.compound.lag_times)
          }
        }
        if (newItem.compound_alias) {
          newItem.compound_alias.is_preferred_synonym = dataFormating.yesno(newItem.is_preferred_synonym)
        }
        if (newItem.strength_value) {
          newItem.strength_value = dataFormating.numericValue(newItem.strength_value)
        }
        result.push(newItem)
      }
      return result
    }
  },
  mounted () {
    this.fetchCompounds()
  },
  watch: {
    options () {
      this.fetchCompounds()
    }
  }
}
</script>
