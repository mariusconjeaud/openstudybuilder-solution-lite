<template>
<v-card data-cy="version-history-window">
  <v-card-title>
    <span class="dialog-title">{{ $t('HistoryTable.title') }} {{ titleLabel }}</span><span v-if="itemName" class="ml-2 dialog-title">[{{ itemName }}]</span><span v-else-if="itemUid" class="ml-2 dialog-title">[{{ itemUid }}]</span>
    <v-spacer/>
    <data-table-export-button
      v-if="urlPrefix"
      :dataUrl="dataUrl"
      />
  </v-card-title>
  <v-card-text>
    <v-data-table
      :headers="headers"
      :items="history"
      dense
      >
      <template v-slot:item="{ item }">
        <tr>
          <td v-for="(header, index)  in headers" v-bind:key="index">
             <div v-if="getHighlight(index, header, item)" class="blue lighten-4 difference">{{ getDisplay(item, header.value) }}</div>
             <span v-else>{{ getDisplay(item, header.value) }}</span>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-card-text>
  <v-card-actions>
    <div class="blue lighten-4 difference">{{ $t('HistoryTable.legend') }}</div>
    <v-spacer></v-spacer>
    <v-btn
      color="secondary"
      @click="close"
      >
      {{ $t('_global.close') }}
    </v-btn>
  </v-card-actions>
</v-card>
</template>

<script>
import { DateTime } from 'luxon'
import { mapGetters } from 'vuex'
import objectiveTemplates from '@/api/objectiveTemplates'
import endpointTemplates from '@/api/endpointTemplates'
import study from '@/api/study'
import timeframeTemplates from '@/api/timeframeTemplates'
import objectives from '@/api/objectives'
import endpoints from '@/api/endpoints'
import timeframes from '@/api/timeframes'
import controlledTerminology from '@/api/controlledTerminology'
import DataTableExportButton from '@/components/tools/DataTableExportButton'
import studyEpochs from '@/api/studyEpochs'
import _isEmpty from 'lodash/isEmpty'
import crfs from '@/api/crfs'
import compounds from '@/api/concepts/compounds'
import compoundAliases from '@/api/concepts/compoundAliases'
import arms from '@/api/arms'

export default {
  props: {
    item: Object,
    type: String,
    titleLabel: String,
    urlPrefix: String,
    urlSuffix: {
      type: String,
      required: false
    }
  },
  components: {
    DataTableExportButton
  },
  data () {
    return {
      history: []
    }
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    dataUrl () {
      if (!this.urlSuffix) {
        return `${this.urlPrefix}${this.itemUid}/versions`
      }
      return `${this.urlPrefix}${this.itemUid}/${this.urlSuffix}/versions`
    },
    itemName () {
      if (this.item && this.item.name && typeof this.item.name === 'string') {
        return this.item.name
      }
      return null
    },
    itemUid () {
      if (this.item) {
        if (this.type === 'codelistSponsorValues') {
          return this.item.codelist_uid
        }
        if (this.type === 'studyObjective' || this.type === 'studyEndpoint') {
          return null
        }
        if (this.type.startsWith('term')) {
          return this.item.term_uid
        }
        return this.item.uid
      }
      return null
    },
    headers () {
      if (this.type === 'studyEpoch') {
        return [
          { text: this.$t('_global.uid'), value: 'uid' },
          { text: this.$t('_global.name'), value: 'epoch_name' },
          { text: this.$t('HistoryTable.change_description'), value: 'change_description' },
          { text: this.$t('StudyEpochTable.number'), value: 'order', width: '5%' },
          { text: this.$t('StudyEpochTable.name'), value: 'epoch_name' },
          { text: this.$t('StudyEpochTable.type'), value: 'epoch_type' },
          { text: this.$t('StudyEpochTable.sub_type'), value: 'epoch_subtype' },
          { text: this.$t('StudyEpochTable.start_rule'), value: 'start_rule' },
          { text: this.$t('StudyEpochTable.end_rule'), value: 'end_rule' },
          { text: this.$t('StudyEpochTable.description'), value: 'description', width: '20%' },
          { text: this.$t('StudyEpochTable.visit_count'), value: 'study_visit_count' },
          { text: this.$t('StudyEpochTable.colour'), value: 'color_hash' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' }
        ]
      }
      if (this.type === 'studyVisit') {
        return [
          { text: this.$t('_global.uid'), value: 'uid' },
          { text: this.$t('StudyVisitForm.study_epoch'), value: 'study_epoch_name' },
          { text: this.$t('StudyVisitsTimeline.visit_type'), value: 'visit_type_name' },
          { text: this.$t('StudyVisitForm.visit_class'), value: 'visit_class' },
          { text: this.$t('StudyVisitForm.anchor_visit_in_group'), value: 'visit_subclass' },
          { text: this.$t('StudyVisitForm.visit_group'), value: 'visit_subname' },
          { text: this.$t('StudyVisitForm.global_anchor_visit'), value: 'is_global_anchor_visit' },
          { text: this.$t('StudyVisitForm.contact_mode'), value: 'visit_contact_mode_name' },
          { text: this.$t('StudyVisitForm.time_reference'), value: 'time_reference_name' },
          { text: this.$t('StudyVisitForm.time_value'), value: 'time_value' },
          { text: this.$t('StudyVisitForm.visit_name'), value: 'visit_name' },
          { text: this.$t('StudyVisitForm.visit_short_name'), value: 'visit_short_name' },
          { text: this.$t('StudyVisitForm.study_day_label'), value: 'study_day_label' },
          { text: this.$t('StudyVisitForm.study_week_label'), value: 'study_week_label' },
          { text: this.$t('StudyVisitForm.visit_window'), value: 'visit_window' },
          { text: this.$t('StudyVisitForm.consecutive_visit'), value: 'consecutive_visit_group' },
          { text: this.$t('StudyVisitForm.show_wisit'), value: 'show_visit' },
          { text: this.$t('StudyVisitForm.visit_description'), value: 'description' },
          { text: this.$t('StudyVisitForm.epoch_allocation'), value: 'epoch_allocation_name' },
          { text: this.$t('StudyVisitForm.visit_start_rule'), value: 'start_rule' },
          { text: this.$t('StudyVisitForm.visit_stop_rule'), value: 'end_rule' },
          { text: this.$t('_global.modified'), value: 'start_date' },
          { text: this.$t('_global.user'), value: 'user_initials' }
        ]
      }
      if (this.type === 'studyActivity') {
        return [
          { text: '#', value: 'order' },
          { text: this.$t('StudyActivity.flowchart_group'), value: 'flowchart_group.sponsor_preferred_name' },
          { text: this.$t('StudyActivity.activity'), value: 'activity.name' },
          { text: this.$t('HistoryTable.change_description'), value: 'change_type' },
          { text: this.$t('_global.status'), value: 'status' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyObjective') {
        return [
          { text: this.$t('StudyObjectivesTable.objective'), value: 'objective.name' },
          { text: this.$t('StudyObjectivesTable.objective_level'), value: 'objective_level.sponsor_preferred_name' },
          { text: this.$t('StudyObjectivesTable.order'), value: 'order' },
          { text: this.$t('HistoryTable.change_description'), value: 'change_type' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyEndpoint') {
        return [
          { text: this.$t('_global.endpoint'), value: 'endpoint.name' },
          { text: this.$t('_global.timeframe'), value: 'timeframe.name' },
          { text: this.$t('StudyEndpointsTable.endpoint_level'), value: 'endpoint_level.sponsor_preferred_name' },
          { text: this.$t('StudyEndpointsTable.order'), value: 'order' },
          { text: this.$t('HistoryTable.change_description'), value: 'change_type' },
          { text: this.$t('_global.status'), value: 'status' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyCriteria') {
        return [
          { text: this.$t('EligibilityCriteriaTable.criteria'), value: 'criteria.name' },
          { text: this.$t('EligibilityCriteriaTable.guidance_text'), value: 'guidance_text' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('HistoryTable.change_description'), value: 'change_type' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyCompoundDosing') {
        return [
          { text: this.$t('StudyCompoundDosingTable.element'), value: 'study_element.name' },
          { text: this.$t('StudyCompoundDosingTable.compound'), value: 'study_compound.compound.name' },
          { text: this.$t('StudyCompoundDosingTable.dose_value'), value: 'dose_value' },
          { text: this.$t('StudyCompoundDosingTable.dose_frequency'), value: 'dose_frequency.name' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyArm') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'short_name' },
          { text: this.$t('HistoryTable.arm_type'), value: 'arm_type' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyBranch') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'short_name' },
          { text: this.$t('HistoryTable.branch_code'), value: 'code' },
          { text: this.$t('HistoryTable.planned_number'), value: 'number_of_subjects' },
          { text: this.$t('HistoryTable.rand_group'), value: 'randomization_group' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyCohort') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'short_name' },
          { text: this.$t('HistoryTable.branch_code'), value: 'code' },
          { text: this.$t('HistoryTable.planned_number'), value: 'number_of_subjects' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'studyElement') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'short_name' },
          { text: this.$t('HistoryTable.element_subtype'), value: 'element_subtype.sponsor_preferred_name' },
          { text: this.$t('HistoryTable.start_rule'), value: 'start_rule' },
          { text: this.$t('HistoryTable.end_rule'), value: 'end_rule' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'termName') {
        return [
          { text: this.$t('HistoryTable.catalogue_name'), value: 'catalogue_name' },
          { text: this.$t('HistoryTable.sponsor_pref_name'), value: 'sponsor_preferred_name' },
          { text: this.$t('_global.status'), value: 'status' },
          { text: this.$t('_global.version'), value: 'version' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      if (this.type === 'termAttributes') {
        return [
          { text: this.$t('HistoryTable.catalogue_name'), value: 'catalogue_name' },
          { text: this.$t('HistoryTable.code_submission_value'), value: 'code_submission_value' },
          { text: this.$t('HistoryTable.name_submission_value'), value: 'name_submission_value' },
          { text: this.$t('HistoryTable.nci_pref_name'), value: 'nci_preferred_name' },
          { text: this.$t('_global.definition'), value: 'definition' },
          { text: this.$t('_global.status'), value: 'status' },
          { text: this.$t('_global.version'), value: 'version' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
          { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
        ]
      }
      return [
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('HistoryTable.change_description'), value: 'change_description' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('_global.user'), value: 'user_initials' },
        { text: this.$t('HistoryTable.start_date'), value: 'start_date' },
        { text: this.$t('HistoryTable.end_date'), value: 'end_date' }
      ]
    }
  },
  methods: {
    close () {
      this.$emit('close')
    },
    /**
     * Fetch version history for given item uid.
     */
    async fetchHistory (item) {
      let resp
      if (!_isEmpty(item)) {
        if (this.type === 'objectiveTemplates') {
          resp = await objectiveTemplates.getVersions(item.uid)
        } else if (this.type === 'endpointTemplates') {
          resp = await endpointTemplates.getVersions(item.uid)
        } else if (this.type === 'objective') {
          resp = await objectives.getVersions(item.uid)
        } else if (this.type === 'timeframeTemplates') {
          resp = await timeframeTemplates.getVersions(item.uid)
        } else if (this.type === 'timeframe') {
          resp = await timeframes.getVersions(item.uid)
        } else if (this.type === 'studyObjective') {
          resp = await study.getStudyObjectiveAuditTrail(this.selectedStudy.uid, item.study_objective_uid)
        } else if (this.type === 'studyEndpoint') {
          resp = await study.getStudyEndpointAuditTrail(this.selectedStudy.uid, item.study_endpoint_uid)
        } else if (this.type === 'codelistSponsorValues') {
          resp = await controlledTerminology.getCodelistNamesVersions(item.codelist_uid)
        } else if (this.type === 'codelistAttributes') {
          resp = await controlledTerminology.getCodelistAttributesVersions(item.codelist_uid)
        } else if (this.type === 'studyEpoch') {
          resp = await studyEpochs.getStudyEpochVersions(this.selectedStudy.uid, item.uid)
        } else if (this.type === 'studyVisit') {
          resp = await studyEpochs.getStudyVisitVersions(this.selectedStudy.uid, item.uid)
        } else if (this.type === 'studyActivity') {
          resp = await study.getStudyActivityAuditTrail(this.selectedStudy.uid, item.study_activity_uid)
        } else if (this.type === 'studyCriteria') {
          resp = await study.getStudyCriteriaAuditTrail(this.selectedStudy.uid, item.study_criteria_uid)
        } else if (this.type === 'crfForm') {
          resp = await crfs.getFormAuditTrail(item.uid)
        } else if (this.type === 'crfGroup') {
          resp = await crfs.getGroupAuditTrail(item.uid)
        } else if (this.type === 'crfItem') {
          resp = await crfs.getItemAuditTrail(item.uid)
        } else if (this.type === 'compound') {
          resp = await compounds.getVersions(item.uid)
        } else if (this.type === 'compoundAlias') {
          resp = await compoundAliases.getVersions(item.uid)
        } else if (this.type === 'studyCompoundDosing') {
          resp = await study.getStudyCompoundDosingAuditTrail(this.selectedStudy.uid, item.study_compound_dosing_uid)
        } else if (this.type === 'studyArm') {
          resp = await studyEpochs.getStudyArmVersions(this.selectedStudy.uid, item.arm_uid)
        } else if (this.type === 'studyBranch') {
          resp = await studyEpochs.getStudyBranchVersions(this.selectedStudy.uid, item.branch_arm_uid)
        } else if (this.type === 'studyCohort') {
          resp = await arms.getStudyCohortVersions(this.selectedStudy.uid, item.cohort_uid)
        } else if (this.type === 'studyElement') {
          resp = await arms.getStudyElementVersions(this.selectedStudy.uid, item.element_uid)
        } else if (this.type === 'termName') {
          resp = await controlledTerminology.getCodelistTermNamesVersions(item.term_uid)
        } else if (this.type === 'termAttributes') {
          resp = await controlledTerminology.getCodelistTermAttributesVersions(item.term_uid)
        } else {
          resp = await endpoints.getVersions(item.uid)
        }
        this.history = resp.data
      }
    },
    getHighlight (index, header, item) {
      if (item) {
        if (header.value.indexOf('Date') !== -1) {
          return false
        } else if (item.changes) {
          return item.changes[header.value]
        } else {
          return false
        }
      }
    },
    getDisplay (item, accessor) {
      const accessList = accessor.split('.')
      if (item) {
        let value = item
        for (const i in accessList) {
          const label = accessList[i]
          if (value) {
            value = value[label]
          }
        }
        if (accessor.indexOf('_date') !== -1) {
          if (value) {
            const originalValue = value
            value = DateTime.fromISO(value).setLocale('en').toLocaleString(DateTime.DATETIME_MED)
            if (value === 'Invalid DateTime') {
              value = originalValue
            }
          }
        }
        if (accessor.indexOf('arm_type') !== -1) {
          if (value) {
            value = value.sponsor_preferred_name
          }
        }
        if (accessor === 'dose_value') {
          value = `${value.value} ${value.unit_label}`
        }
        return value
      }
    }
  },
  mounted () {
    if ('item' in this && this.item) {
      this.fetchHistory(this.item)
    }
  },
  watch: {
    item: {
      handler (value) {
        if (value) {
          this.fetchHistory(value)
        }
      },
      immediate: true
    }
  }
}
</script>

<style scoped>
  .difference,
  .history-info {
    display: flex;
    justify-content: center;
    flex-direction: column;
    padding: 0 10px;
    border-radius: 12px;
    height: 60px;
    margin: 10px 0;
  }
</style>
