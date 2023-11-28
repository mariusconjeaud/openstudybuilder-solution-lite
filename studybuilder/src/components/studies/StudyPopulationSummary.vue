<template>
<study-metadata-summary
  :metadata="metadata"
  :params="params"
  :first-col-label="$t('StudyPopulationSummary.info_column')"
  persistent-dialog
  copy-from-study
  component="study_population"
  >
  <template v-slot:form="{ closeHandler, dataToCopy, openHandler }">
    <study-population-form :open="openHandler" :metadata="(Object.keys(dataToCopy).length !== 0) ? dataToCopy : metadata" @updated="onMetadataUpdated" @close="closeHandler" :debug="true" />
  </template>
</study-metadata-summary>
</template>

<script>
import { mapGetters } from 'vuex'
import study from '@/api/study'
import StudyMetadataSummary from './StudyMetadataSummary'
import StudyPopulationForm from './StudyPopulationForm'

export default {
  components: {
    StudyMetadataSummary,
    StudyPopulationForm
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
          label: this.$t('StudyPopulationForm.therapeuticarea'),
          name: 'therapeutic_area_codes',
          valuesDisplay: 'terms'
        },
        {
          label: this.$t('StudyPopulationForm.disease_condition'),
          name: 'disease_condition_or_indication_codes',
          valuesDisplay: 'terms'
        },
        {
          label: this.$t('StudyPopulationForm.stable_disease_min_duration'),
          name: 'stable_disease_minimum_duration',
          valuesDisplay: 'duration'
        },
        {
          label: this.$t('StudyPopulationForm.healthy_subjects'),
          name: 'healthy_subject_indicator',
          valuesDisplay: 'yesno'
        },
        {
          label: this.$t('StudyPopulationForm.diagnosis_group'),
          name: 'diagnosis_group_codes',
          valuesDisplay: 'terms'
        },
        {
          label: this.$t('StudyPopulationForm.relapse_criteria'),
          name: 'relapse_criteria'
        },
        {
          label: this.$t('StudyPopulationForm.number_of_expected_subjects'),
          name: 'number_of_expected_subjects'
        },
        {
          label: this.$t('StudyPopulationForm.rare_disease_indicator'),
          name: 'rare_disease_indicator',
          valuesDisplay: 'yesno'
        },
        {
          label: this.$t('StudyPopulationForm.sex_of_study_participants'),
          name: 'sex_of_participants_code',
          valuesDisplay: 'terms'
        },
        {
          label: this.$t('StudyPopulationForm.planned_min_age'),
          name: 'planned_minimum_age_of_subjects',
          valuesDisplay: 'duration'
        },
        {
          label: this.$t('StudyPopulationForm.planned_max_age'),
          name: 'planned_maximum_age_of_subjects',
          valuesDisplay: 'duration'
        },
        {
          label: this.$t('StudyPopulationForm.pediatric_study_indicator'),
          name: 'pediatric_study_indicator',
          valuesDisplay: 'yesno'
        },
        {
          label: this.$t('StudyPopulationForm.pediatric_investigation_plan_indicator'),
          name: 'pediatric_investigation_plan_indicator',
          valuesDisplay: 'yesno'
        },
        {
          label: this.$t('StudyPopulationForm.pediatric_postmarket_study_indicator'),
          name: 'pediatric_postmarket_study_indicator',
          valuesDisplay: 'yesno'
        }
      ]
    }
  },
  methods: {
    onMetadataUpdated (metadata) {
      this.metadata = metadata
    }
  },
  created () {
    this.$store.dispatch('studiesGeneral/fetchUnits')
    this.$store.dispatch('studiesGeneral/fetchSnomedTerms')
    this.$store.dispatch('studiesGeneral/fetchSexOfParticipants')
    study.getStudyPopulationMetadata(this.selectedStudy.uid, this.selectedStudyVersion).then(resp => {
      this.metadata = resp.data.current_metadata.study_population
    })
  }
}
</script>
