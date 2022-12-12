<template>
<v-card data-cy="version-history-window">
  <v-card-title>
    <span class="dialog-title">{{ titleLabel }} {{ $t('HistoryTable.history') }} {{ $t('HistoryTable.for_study') }} {{ selectedStudy.studyId }}</span>
    <v-spacer/>
    <data-table-export-button
      v-if="urlPrefix"
      :type="type"
      :dataUrl="`${urlPrefix}${itemUid}/versions`"
      />
  </v-card-title>
  <v-card-text>
    <v-data-table
      :headers="headers"
      :items="history"
      dense
      sort-by="start_date"
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
import DataTableExportButton from '@/components/tools/DataTableExportButton'
import studyEpochs from '@/api/studyEpochs'
import arms from '@/api/arms'

export default {
  props: {
    type: String,
    titleLabel: String,
    urlPrefix: String
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
    itemUid () {
      if (this.item) {
        return this.item.uid
      }
      return null
    },
    headers () {
      if (this.type === 'studyArms') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'shortName' },
          { text: this.$t('HistoryTable.arm_type'), value: 'armType' },
          { text: this.$t('HistoryTable.number_of_subj'), value: 'number_of_subjects' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('HistoryTable.change_type'), value: 'changeType' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.valid_from'), value: 'start_date' },
          { text: this.$t('HistoryTable.valid_to'), value: 'endDate' }
        ]
      }
      if (this.type === 'studyBranches') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'shortName' },
          { text: this.$t('HistoryTable.branch_code'), value: 'code' },
          { text: this.$t('HistoryTable.planned_number'), value: 'number_of_subjects' },
          { text: this.$t('HistoryTable.rand_group'), value: 'randomization_group' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('HistoryTable.change_type'), value: 'changeType' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.valid_from'), value: 'start_date' },
          { text: this.$t('HistoryTable.valid_to'), value: 'endDate' }
        ]
      }
      if (this.type === 'studyCohorts') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'shortName' },
          { text: this.$t('HistoryTable.branch_code'), value: 'code' },
          { text: this.$t('HistoryTable.arms_uids'), value: 'armRootsUids' },
          { text: this.$t('HistoryTable.branches_uids'), value: 'branchArmRootsUids' },
          { text: this.$t('HistoryTable.planned_number'), value: 'number_of_subjects' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('HistoryTable.change_type'), value: 'changeType' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.valid_from'), value: 'start_date' },
          { text: this.$t('HistoryTable.valid_to'), value: 'endDate' }
        ]
      }
      if (this.type === 'studyElements') {
        return [
          { text: this.$t('_global.name'), value: 'name' },
          { text: this.$t('HistoryTable.short_name'), value: 'shortName' },
          { text: this.$t('HistoryTable.element_subtype'), value: 'elementSubType.sponsor_preferred_name' },
          { text: this.$t('HistoryTable.planned_duration'), value: 'plannedDuration' },
          { text: this.$t('HistoryTable.start_rule'), value: 'startRule' },
          { text: this.$t('HistoryTable.end_rule'), value: 'endRule' },
          { text: this.$t('_global.order'), value: 'order' },
          { text: this.$t('_global.description'), value: 'description' },
          { text: this.$t('HistoryTable.change_type'), value: 'changeType' },
          { text: this.$t('_global.user'), value: 'user_initials' },
          { text: this.$t('HistoryTable.valid_from'), value: 'start_date' },
          { text: this.$t('HistoryTable.valid_to'), value: 'endDate' }
        ]
      }
      if (this.type === 'studyEpochs') {
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
      if (this.type === 'studyVisits') {
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
      return [
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('_global.name'), value: 'name' },
        { text: this.$t('HistoryTable.change_description'), value: 'change_description' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' },
        { text: this.$t('HistoryTable.change_type'), value: 'changeType' },
        { text: this.$t('_global.user'), value: 'user_initials' },
        { text: this.$t('HistoryTable.valid_from'), value: 'start_date' },
        { text: this.$t('HistoryTable.valid_to'), value: 'endDate' }
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
    async fetchHistory () {
      let resp
      if (this.type === 'studyArms') {
        resp = await studyEpochs.getStudyArmsVersions(this.selectedStudy.uid)
      } else if (this.type === 'studyBranches') {
        resp = await studyEpochs.getStudyBranchesVersions(this.selectedStudy.uid)
      } else if (this.type === 'studyCohorts') {
        resp = await arms.getStudyCohortsVersions(this.selectedStudy.uid)
      } else if (this.type === 'studyElements') {
        resp = await arms.getStudyElementsVersions(this.selectedStudy.uid)
      } else if (this.type === 'studyEpochs') {
        resp = await studyEpochs.getStudyEpochsVersions(this.selectedStudy.uid)
      } else if (this.type === 'studyVisits') {
        resp = await studyEpochs.getStudyVisitsVersions(this.selectedStudy.uid)
      }
      this.history = resp.data
    },
    getHighlight (index, header, item) {
      if (item) {
        if (header.value.indexOf('Date') !== -1 || header.value.indexOf('changeType') !== -1) {
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
        if (accessor.indexOf('Date') !== -1) {
          if (value) {
            value = DateTime.fromISO(value).setLocale('en').toLocaleString(DateTime.DATETIME_MED)
          }
        }
        if (accessor.indexOf('armType') !== -1) {
          if (value) {
            value = value.sponsor_preferred_name
          }
        }
        if (accessor.indexOf('armRootsUids') !== -1) {
          if (value) {
            value = value.join(', ')
          }
        }
        if (accessor.indexOf('branchArmRootsUids') !== -1) {
          if (value) {
            value = value.join(', ')
          }
        }
        if (accessor.indexOf('plannedDuration') !== -1) {
          if (value) {
            value = value.durationValue + ' ' + value.durationUnitCode.name
          }
        }
        return value
      }
    }
  },
  mounted () {
    this.fetchHistory(this.item)
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
