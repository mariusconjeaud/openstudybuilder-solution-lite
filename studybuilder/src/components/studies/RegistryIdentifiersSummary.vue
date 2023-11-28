<template>
<study-metadata-summary
  :metadata="identifiers"
  :params="params"
  :first-col-label="$t('StudyRegistryIdentifiersSummary.registry_identifiers')"
  :fullscreen-form="false"
  form-max-width="1000px"
  component="registry_identifiers"
  >
  <template v-slot:form="{ closeHandler, openHandler }">
    <registry-identifiers-form
      :open="openHandler"
      @close="closeHandler"
      @updated="onIdentifiersUpdated"
      :identifiers="identifiers"
      />
  </template>
</study-metadata-summary>
</template>

<script>
import { mapGetters } from 'vuex'
import study from '@/api/study'
import RegistryIdentifiersForm from './RegistryIdentifiersForm'
import StudyMetadataSummary from './StudyMetadataSummary'

export default {
  components: {
    RegistryIdentifiersForm,
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
      identifiers: {},
      params: [
        {
          label: this.$t('RegistryIdentifiersForm.ctgovid'),
          name: 'ct_gov_id',
          nullValueName: 'ct_gov_id_null_value_code'
        },
        {
          label: this.$t('RegistryIdentifiersForm.eudractid'),
          name: 'eudract_id',
          nullValueName: 'eudract_id_null_value_code'
        },
        {
          label: this.$t('RegistryIdentifiersForm.utn'),
          name: 'universal_trial_number_utn',
          nullValueName: 'universal_trial_number_utn_null_value_code'
        },
        {
          label: this.$t('RegistryIdentifiersForm.japic'),
          name: 'japanese_trial_registry_id_japic',
          nullValueName: 'japanese_trial_registry_id_japic_null_value_code'
        },
        {
          label: this.$t('RegistryIdentifiersForm.ind'),
          name: 'investigational_new_drug_application_number_ind',
          nullValueName: 'investigational_new_drug_application_number_ind_null_value_code'
        }
      ]
    }
  },
  methods: {
    onIdentifiersUpdated (identifiers) {
      this.identifiers = identifiers
    }
  },
  mounted () {
    this.$store.dispatch('studiesGeneral/fetchNullValues')
    study.getStudy(this.selectedStudy.uid, false, this.selectedStudyVersion).then(resp => {
      this.identifiers = resp.data.current_metadata.identification_metadata.registry_identifiers
    })
  }
}
</script>
