<template>
<div>
  <n-n-table
    :headers="headers"
    :items="computedParams"
    item-key="name"
    :itemsPerPage="15"
    disable-filtering
    hide-export-button
    hide-default-switches
    >
    <template v-slot:actions="">
      <slot
        name="topActions"
        >
      </slot>
      <v-btn
        v-if="copyFromStudy"
        color="primary"
        data-cy="copy-from-study"
        fab
        small
        @click.stop="openCopyForm"
        :title="$t('NNTableTooltips.copy_from_study')"
        >
        <v-icon>mdi-content-copy</v-icon>
      </v-btn>
      <v-btn
        fab
        small
        class="ml-2"
        color="primary"
        @click.stop="openForm"
        :title="$t('NNTableTooltips.edit_content')"
        data-cy="edit-content"
        >
        <v-icon>
          mdi-pencil
        </v-icon>
      </v-btn>
      <v-btn
        class="ml-2"
        color="secondary"
        fab
        small
        :title="$t('NNTableTooltips.history')"
        @click="openHistory"
        >
        <v-icon>mdi-history</v-icon>
      </v-btn>
    </template>
  </n-n-table>
  <slot name="form" :openHandler="showForm" v-bind:closeHandler="closeForm" v-bind:data="metadata" v-bind:dataToCopy="dataToCopy"></slot>

  <v-dialog
    v-model="showCopyForm"
    @keydown.esc="closeCopyForm"
    persistent
    max-width="500px"
    >
    <copy-from-study-form @close="closeCopyForm" @apply="openFormToCopy" :component="component"/>
  </v-dialog>

  <v-dialog
    v-model="showHistory"
    @keydown.esc="closeHistory"
    persistent
    max-width="1200px"
    >
    <history-table
      :headers="historyHeaders"
      :items="historyItems"
      :title="historyTitle"
      :export-name="component"
      @close="closeHistory"
      start-date-header="date"
      change-type-header="action"
      />
  </v-dialog>
</div>
</template>

<script>
import CopyFromStudyForm from '@/components/tools/CopyFromStudyForm'
import HistoryTable from '@/components/tools/HistoryTable'
import { mapGetters } from 'vuex'
import NNTable from '@/components/tools/NNTable'
import study from '@/api/study'

export default {
  components: {
    HistoryTable,
    NNTable,
    CopyFromStudyForm
  },
  props: {
    params: Array,
    metadata: Object,
    firstColLabel: String,
    persistentDialog: {
      type: Boolean,
      default: false
    },
    formMaxWidth: {
      type: String,
      required: false
    },
    copyFromStudy: {
      type: Boolean,
      default: false
    },
    component: String,
    withReasonForMissing: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      studyTypes: 'studiesGeneral/studyTypes',
      trialIntentTypes: 'studiesGeneral/trialIntentTypes',
      trialTypes: 'studiesGeneral/trialTypes',
      trialPhases: 'studiesGeneral/trialPhases',
      therapeuticAreas: 'studiesGeneral/therapeuticAreas',
      diseaseConditions: 'studiesGeneral/diseaseConditions',
      sexOfParticipants: 'studiesGeneral/sexOfParticipants',
      diagnosisGroups: 'studiesGeneral/diagnosisGroups',
      controlTypes: 'studiesGeneral/controlTypes',
      interventionModels: 'studiesGeneral/interventionModels',
      trialBlindingSchemas: 'studiesGeneral/trialBlindingSchemas',
      nullValues: 'studiesGeneral/nullValues'
    }),
    computedParams () {
      return this.buildTableParams(this.params)
    },
    historyTitle () {
      return `${this.component} ${this.$t('HistoryTable.fields')} ${this.$t('HistoryTable.history')} (${this.selectedStudy.uid})`
    },
    exportDataUrl () {
      return `studies/${this.selectedStudy.uid}`
    }
  },
  data () {
    const headers = [
      { text: this.firstColLabel, value: 'name', width: '30%' },
      { text: this.$t('StudyMetadataSummary.selected_values'), value: 'values' }
    ]
    if (this.withReasonForMissing) {
      headers.push(
        { text: this.$t('StudyMetadataSummary.reason_for_missing'), value: 'reason_for_missing' }
      )
    }
    return {
      headers,
      historyHeaders: [
        { text: this.$t('HistoryTable.field'), value: 'field' },
        { text: this.$t('HistoryTable.value_before'), value: 'before_value.term_uid' },
        { text: this.$t('HistoryTable.value_after'), value: 'after_value.term_uid' },
        { text: this.$t('_global.user'), value: 'user_initials' }
      ],
      historyItems: [],
      showHistory: false,
      showForm: false,
      showCopyForm: false,
      dataToCopy: {}
    }
  },
  methods: {
    openForm () {
      this.showForm = true
    },
    closeForm () {
      this.showForm = false
    },
    openFormToCopy (data) {
      this.dataToCopy = data
      this.showForm = true
      this.showCopyForm = false
    },
    openCopyForm () {
      this.showCopyForm = true
    },
    closeCopyForm () {
      this.showCopyForm = false
    },
    async openHistory () {
      this.historyItems = []
      const resp = await study.getStudyFieldsAuditTrail(this.selectedStudy.uid, this.component)
      for (const group of resp.data) {
        for (const groupItem of group.actions) {
          const row = {
            user_initials: group.user_initials,
            date: group.date,
            field: groupItem.field,
            action: groupItem.action,
            before_value: groupItem.before_value,
            after_value: groupItem.after_value
          }
          this.historyItems.push(row)
        }
      }
      this.showHistory = true
    },
    closeHistory () {
      this.showHistory = false
    },
    buildTableParams (fields) {
      const result = []
      fields.forEach(field => {
        let nullValueName = null
        if (field.nullValueName === undefined) {
          nullValueName = field.name
          const suffixes = ['_code', '_codes']
          suffixes.forEach(suffix => {
            if (nullValueName.endsWith(suffix)) {
              nullValueName = nullValueName.replace(suffix, '')
            }
          })
          nullValueName += '_null_value_code'
        } else {
          nullValueName = field.nullValueName
        }
        let values = this.metadata[field.name]
        if (field.name === 'sex_of_participants_code' && values !== undefined && values !== null) {
          values = values.name
        }
        result.push({
          name: field.label,
          values: (values !== undefined && values !== null && field.valuesDisplay && field.name !== 'sex_of_participants_code') ? this[`${field.valuesDisplay}Display`](values) : values,
          reason_for_missing: this.naDisplay(this.metadata[nullValueName])
        })
      })
      return result
    },
    yesnoDisplay (value) {
      return (value) ? this.$t('_global.yes') : this.$t('_global.no')
    },
    durationDisplay (value) {
      return `${value.duration_value} ${value.duration_unit_code.name}`
    },
    termDisplay (value) {
      if (!value) {
        return ''
      }
      return value.name
    },
    termsDisplay (value) {
      const result = value.map(item => item.name)
      return result.join(', ')
    },
    naDisplay (value) {
      if (value) {
        return value.name
      }
    }
  }
}
</script>
