<template>
<div>
  <study-metadata-summary
    :metadata="identification"
    :params="params"
    :first-col-label="$t('StudyIdentificationSummary.core_attribute')"
    :fullscreen-form="false"
    form-max-width="1000px"
    component="identification_metadata"
    :with-reason-for-missing="false"
    >
    <template v-slot:topActions>
      <v-btn
        v-if="canDeleteSelectedStudy()"
        fab
        small
        dark
        color="red"
        @click.stop="deleteStudy"
        :title="$t('_global.delete')"
        >
        <v-icon>mdi-trash-can</v-icon>
      </v-btn>
    </template>
    <template v-slot:form="{ closeHandler, openHandler }">
      <study-form
        :open="openHandler"
        @close="close(closeHandler)"
        :edited-study="study"
        @updated="onIdentificationUpdated"
        />
    </template>
  </study-metadata-summary>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import { mapGetters } from 'vuex'
import api from '@/api/study'
import StudyForm from './StudyForm'
import StudyMetadataSummary from './StudyMetadataSummary'

export default {
  components: {
    ConfirmDialog,
    StudyForm,
    StudyMetadataSummary
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      identification: {},
      params: [
        {
          label: this.$t('Study.clinical_programme'),
          name: 'clinical_programme_name'
        },
        {
          label: this.$t('Study.project_number'),
          name: 'project_number'
        },
        {
          label: this.$t('Study.project_name'),
          name: 'project_name'
        },
        {
          label: this.$t('Study.study_id'),
          name: 'study_id'
        },
        {
          label: this.$t('Study.study_number'),
          name: 'study_number'
        },
        {
          label: this.$t('Study.study_acronym'),
          name: 'study_acronym'
        }
      ],
      study: null
    }
  },
  mounted () {
    api.getStudy(this.selectedStudy.uid).then(resp => {
      this.study = resp.data
      this.identification = resp.data.current_metadata.identification_metadata
    })
  },
  methods: {
    canDeleteSelectedStudy () {
      return this.study && this.study.possible_actions.find(action => action === 'delete')
    },
    async deleteStudy () {
      const options = { type: 'warning' }
      const study = this.study.current_metadata.identification_metadata.study_id
      if (await this.$refs.confirm.open(this.$t('StudyStatusTable.confirm_delete', { study }), options)) {
        await api.deleteStudy(this.selectedStudy.uid)
        bus.$emit('notification', { msg: this.$t('StudyStatusTable.delete_success'), type: 'success' })
        this.$store.commit('studiesGeneral/UNSELECT_STUDY')
        this.$router.push({ name: 'SelectOrAddStudy' })
      }
    },
    close (closeHandler) {
      this.study = null
      closeHandler()
    },
    onIdentificationUpdated (data) {
      this.study = data
      this.identification = data.current_metadata.identification_metadata
    }
  }
}
</script>
