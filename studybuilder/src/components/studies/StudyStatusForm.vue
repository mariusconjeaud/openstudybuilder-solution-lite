<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="close"
  @submit="submit"
  :open="open"
  max-width="1200px"
  >
  <template v-slot:body>
    <v-data-table
      :headers="headers"
      :items="items"
      hide-default-footer
      class="mb-10"
      />

    <validation-observer ref="observer">
      <v-row>
        <v-col cols="12">
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-textarea
              :label="$t('Study.release_description')"
              data-cy="release-description"
              v-model="form.change_description"
              :error-messages="errors"
              hide-details
              class="mt-10"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import api from '@/api/study'
import { bus } from '@/main'
import { mapGetters } from 'vuex'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    action: String,
    helpItems: [],
    open: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      return (this.action === 'release') ? this.$t('StudyStatusForm.release_title') : this.$t('StudyStatusForm.lock_title')
    },
    items () {
      return [this.selectedStudy]
    }
  },
  data () {
    return {
      form: {},
      headers: [
        { text: this.$t('Study.status'), value: 'current_metadata.version_metadata.study_status' },
        { text: this.$t('Study.clinical_programme'), value: 'current_metadata.identification_metadata.clinical_programme_name' },
        { text: this.$t('Study.project_number'), value: 'current_metadata.identification_metadata.project_number' },
        { text: this.$t('Study.project_name'), value: 'current_metadata.identification_metadata.project_name' },
        { text: this.$t('Study.study_number'), value: 'current_metadata.identification_metadata.study_number' },
        { text: this.$t('Study.acronym'), value: 'current_metadata.identification_metadata.study_acronym' }
      ]
    }
  },
  methods: {
    close () {
      this.form = {}
      this.$refs.observer.reset()
      this.$emit('close')
    },
    async submit () {
      try {
        if (this.action === 'release') {
          await api.releaseStudy(this.selectedStudy.uid, this.form)
          bus.$emit('notification', { msg: this.$t('StudyStatusForm.release_success'), type: 'success' })
        } else {
          const resp = await api.lockStudy(this.selectedStudy.uid, this.form)
          this.$store.commit('studiesGeneral/SELECT_STUDY', { studyObj: resp.data })
          bus.$emit('notification', { msg: this.$t('StudyStatusForm.lock_success'), type: 'success' })
        }
        this.$emit('statusChanged')
        this.close()
      } finally {
        this.$refs.form.working = false
      }
    }
  }
}
</script>
