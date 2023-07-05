<template>
<div>
  <n-n-table
    :headers="headers"
    :items="formatedStudyCompoudDosings"
    item-key="study_compound_dosing_uid"
    export-object-label="StudyCompoundDosings"
    :export-data-url="exportDataUrl"
    column-data-resource="study-compound-dosings"
    :history-data-fetcher="fetchCompoundDosingsHistory"
    :history-title="$t('StudyCompoundDosingTable.global_history_title')"
    >
    <template v-slot:actions="">
      <v-btn
        data-cy="add-study-compound-dosing"
        fab
        small
        color="primary"
        @click.stop="showForm = true"
        :title="$t('StudyCompoundForm.add_title')"
        >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
    </template>
    <template v-slot:item.actions="{ item }">
      <actions-menu :actions="actions" :item="item" />
    </template>
  </n-n-table>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
  <v-dialog
    v-model="showForm"
    persistent
    fullscreen
    content-class="fullscreen-dialog"
    >
    <compound-dosing-form
      @close="closeForm"
      :study-compound-dosing="selectedStudyCompoundDosing"
      />
  </v-dialog>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import ActionsMenu from '@/components/tools/ActionsMenu'
import CompoundDosingForm from './CompoundDosingForm'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import dataFormating from '@/utils/dataFormating'
import NNTable from '@/components/tools/NNTable'
import study from '@/api/study'

export default {
  components: {
    ActionsMenu,
    CompoundDosingForm,
    ConfirmDialog,
    NNTable
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyCompoundDosings: 'studyCompounds/studyCompoundDosings'
    }),
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}/study-compound-dosings`
    },
    formatedStudyCompoudDosings () {
      return this.transformItems(this.studyCompoundDosings)
    },
    studyCompoundDosingHistoryTitle () {
      if (this.selectedStudyCompoundDosing) {
        return this.$t(
          'StudyCompoundDosingTable.study_compound_dosing_history_title',
          { studyCompoundDosingUid: this.selectedStudyCompoundDosing.study_compound_dosing_uid })
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
          click: this.editStudyCompoundDosing
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete',
          iconColor: 'error',
          click: this.deleteStudyCompoundDosing
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openHistory
        }
      ],
      headers: [
        { text: '', value: 'actions', width: '5%' },
        { text: '#', value: 'order' },
        { text: this.$t('StudyCompoundDosingTable.element'), value: 'study_element.name' },
        { text: this.$t('StudyCompoundDosingTable.compound'), value: 'study_compound.compound.name' },
        { text: this.$t('StudyCompoundDosingTable.compound_alias'), value: 'study_compound.compound_alias.name' },
        { text: this.$t('StudyCompoundDosingTable.preferred_alias'), value: 'study_compound.compound_alias.is_preferred_synonym' },
        { text: this.$t('StudyCompoundDosingTable.dose_value'), value: 'dose_value' },
        { text: this.$t('StudyCompoundDosingTable.dose_frequency'), value: 'dose_frequency.name' }
      ],
      selectedStudyCompoundDosing: null,
      showForm: false,
      showHistory: false,
      compoundDosingHistoryItems: []
    }
  },
  methods: {
    async deleteStudyCompoundDosing (studyCompoundDosing) {
      const options = { type: 'warning' }
      const compound = studyCompoundDosing.study_compound.compound_alias.name
      const element = studyCompoundDosing.study_element.name
      const msg = this.$t('StudyCompoundDosingTable.confirm_delete', { compound, element })
      if (!await this.$refs.confirm.open(msg, options)) {
        return
      }
      this.$store.dispatch('studyCompounds/deleteStudyCompoundDosing', {
        studyUid: this.selectedStudy.uid,
        studyCompoundDosingUid: studyCompoundDosing.study_compound_dosing_uid
      }).then(resp => {
        bus.$emit('notification', { msg: this.$t('StudyCompoundDosingTable.delete_success') })
      })
    },
    editStudyCompoundDosing (studyCompoundDosing) {
      this.selectedStudyCompoundDosing = studyCompoundDosing
      this.showForm = true
    },
    async fetchCompoundDosingsHistory () {
      const resp = await study.getStudyCompoundDosingsAuditTrail(this.selectedStudy.uid)
      return this.transformItems(resp.data)
    },
    async openHistory (studyCompoundDosing) {
      this.selectedStudyCompoundDosing = studyCompoundDosing
      const resp = await study.getStudyCompoundDosingAuditTrail(this.selectedStudy.uid, studyCompoundDosing.study_compound_dosing_uid)
      this.compoundDosingHistoryItems = this.transformItems(resp.data)
      this.showHistory = true
    },
    closeHistory () {
      this.selectedStudyCompoundDosing = null
      this.showHistory = false
    },
    closeForm () {
      this.showForm = false
      this.selectedStudyCompoundDosing = null
    },
    transformItems (items) {
      const result = []
      for (const item of items) {
        const newItem = { ...item }
        if (newItem.study_compound.compound_alias) {
          newItem.study_compound.compound_alias.is_preferred_synonym = dataFormating.yesno(newItem.study_compound.compound_alias.is_preferred_synonym)
        }
        if (newItem.dose_value) {
          newItem.dose_value = dataFormating.numericValue(newItem.dose_value)
        }
        result.push(newItem)
      }
      return result
    }
  },
  mounted () {
    this.$store.dispatch('studyCompounds/fetchStudyCompoundDosings', this.selectedStudy.uid)
  }
}
</script>
