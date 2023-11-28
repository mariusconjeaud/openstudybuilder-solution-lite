<template>
<study-activity-selection-base-form
  ref="baseForm"
  :help-items="helpItems"
  :selection="selection"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <validation-provider
        v-slot="{ errors }"
        name="visits"
        rules="required"
        >
        <v-autocomplete
          v-model="selectedVisits"
          :items="studyVisits"
          :label="$t('StudyActivityScheduleBatchEditForm.studyVisits')"
          item-text="visit_short_name"
          return-object
          multiple
          clearable
          :error-messages="errors"
          class="mt-4"
          />
      </validation-provider>
    </validation-observer>
  </template>
</study-activity-selection-base-form>
</template>

<script>
import { bus } from '@/main'
import { mapGetters } from 'vuex'
import study from '@/api/study'
import StudyActivitySelectionBaseForm from './StudyActivitySelectionBaseForm'
import studyEpochs from '@/api/studyEpochs'

export default {
  components: {
    StudyActivitySelectionBaseForm
  },
  props: {
    selection: Array,
    currentSelectionMatrix: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  data () {
    return {
      helpItems: [],
      selectedVisits: [],
      studyVisits: []
    }
  },
  methods: {
    close () {
      this.$emit('close')
      this.selectedVisits = []
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      this.$refs.baseForm.loading = true
      const data = []
      for (const item of this.selection) {
        // First: delete any existing study activity schedule for the given selection
        for (const cell of Object.values(this.currentSelectionMatrix[item.study_activity_uid])) {
          if (cell.uid) {
            this.$set(cell, 'value', false)
            data.push({
              method: 'DELETE',
              content: { uid: cell.uid }
            })
          }
        }
        // Second: create new activity schedules
        for (const visit of this.selectedVisits) {
          this.$set(this.currentSelectionMatrix[item.study_activity_uid][visit.uid], 'value', true)
          data.push({
            method: 'POST',
            content: {
              study_activity_uid: item.study_activity_uid,
              study_visit_uid: visit.uid
            }
          })
        }
      }
      study.studyActivityScheduleBatchOperations(this.selectedStudy.uid, data).then(resp => {
        bus.$emit('notification', { type: 'success', msg: this.$t('DetailedFlowchart.update_success') })
        this.$emit('updated')
        this.close()
        this.$refs.baseForm.loading = false
      }, _err => {
        this.$refs.baseForm.loading = false
      })
    }
  },
  mounted () {
    // Only retrieve ungrouped visits since groups are already used
    // for batch operations...
    const params = {
      page_size: 0,
      study_value_version: this.selectedStudyVersion,
      filters: {
        consecutive_visit_group: { v: [null], op: 'eq' }
      }
    }
    studyEpochs.getStudyVisits(this.selectedStudy.uid, params).then(resp => {
      this.studyVisits = resp.data.items
    })
  }
}
</script>
