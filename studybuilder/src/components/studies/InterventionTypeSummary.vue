<template>
<study-metadata-summary
  :metadata="metadata"
  :params="params"
  :first-col-label="$t('StudyInterventionTypeSummary.intervention_type_info')"
  persistent-dialog
  copy-from-study
  component="study_intervention"
  >
  <template v-slot:form="{ closeHandler, dataToCopy, openHandler }">
    <intervention-type-form :open="openHandler" :metadata="(Object.keys(dataToCopy).length !== 0) ? dataToCopy : metadata" @updated="onMetadataUpdated" @close="closeHandler" />
  </template>
</study-metadata-summary>
</template>

<script>
import { mapGetters } from 'vuex'
import study from '@/api/study'
import InterventionTypeForm from './InterventionTypeForm'
import StudyMetadataSummary from './StudyMetadataSummary'

export default {
  components: {
    InterventionTypeForm,
    StudyMetadataSummary
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy',
      selectedStudyVersion: 'studiesGeneral/selectedStudyVersion'
    })
  },
  data () {
    return {
      metadata: {},
      params: [
        {
          label: this.$t('StudyInterventionTypeForm.intervention_type'),
          name: 'intervention_type_code',
          valuesDisplay: 'term'
        },
        {
          label: this.$t('StudyDefineForm.studyintent'),
          name: 'trial_intent_types_codes',
          valuesDisplay: 'terms'
        },
        {
          label: this.$t('StudyInterventionTypeForm.added_to_et'),
          name: 'add_on_to_existing_treatments',
          valuesDisplay: 'yesno'
        },
        {
          label: this.$t('StudyInterventionTypeForm.control_type'),
          name: 'control_type_code',
          valuesDisplay: 'term'
        },
        {
          label: this.$t('StudyInterventionTypeForm.intervention_model'),
          name: 'intervention_model_code',
          valuesDisplay: 'term'
        },
        {
          label: this.$t('StudyInterventionTypeForm.randomised'),
          name: 'is_trial_randomised',
          valuesDisplay: 'yesno'
        },
        { label: this.$t('StudyInterventionTypeForm.strfactor'), name: 'stratification_factor' },
        {
          label: this.$t('StudyInterventionTypeForm.blinding_schema'),
          name: 'trial_blinding_schema_code',
          valuesDisplay: 'term'
        },
        {
          label: this.$t('StudyInterventionTypeForm.planned_st_length'),
          name: 'planned_study_length',
          valuesDisplay: 'duration'
        }
      ]
    }
  },
  methods: {
    onMetadataUpdated (metadata) {
      this.metadata = metadata
    }
  },
  mounted () {
    this.$store.dispatch('studiesGeneral/fetchUnits')
    this.$store.dispatch('studiesGeneral/fetchTrialBlindingSchemas')
    this.$store.dispatch('studiesGeneral/fetchControlTypes')
    this.$store.dispatch('studiesGeneral/fetchInterventionModels')
    this.$store.dispatch('studiesGeneral/fetchTrialIntentTypes')
    this.$store.dispatch('studiesGeneral/fetchInterventionTypes')
    study.getStudyInterventionMetadata(this.selectedStudy.uid, this.selectedStudyVersion).then(resp => {
      this.metadata = resp.data.current_metadata.study_intervention
    })
  }
}
</script>
