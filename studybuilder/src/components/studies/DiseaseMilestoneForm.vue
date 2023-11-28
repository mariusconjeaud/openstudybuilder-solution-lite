<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  :help-text="$t('_help.StudyDefineForm.general')"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <v-row>
        <v-col>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-autocomplete
              v-model="form.disease_milestone_type"
              :label="$t('DiseaseMilestone.disease_milestone_type')"
              data-cy="disease-milestone-type"
              :items="diseaseMilestoneTypes"
              item-text="sponsor_preferred_name"
              item-value="term_uid"
              :error-messages="errors"
              clearable
              class="required"
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-checkbox
            v-model="form.repetition_indicator"
            :label="$t('DiseaseMilestone.repetition_indicator')"
            data-cy="repetition-indicator"
            />
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import { bus } from '@/main'
import { mapGetters } from 'vuex'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import study from '@/api/study'
import terms from '@/api/controlledTerminology/terms'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    diseaseMilestone: Object,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      return (this.diseaseMilestone) ? this.$t('DiseaseMilestoneForm.edit_title') : this.$t('DiseaseMilestoneForm.add_title')
    }
  },
  data () {
    return {
      diseaseMilestoneTypes: [],
      form: {},
      helpItems: [
        'DiseaseMilestone.disease_milestone_type',
        'DiseaseMilestone.repetition_indicator'
      ]
    }
  },
  methods: {
    close () {
      this.$emit('close')
      this.form = {}
      this.$refs.observer.reset()
    },
    async submit () {
      const data = { ...this.form }
      data.study_uid = this.selectedStudy.uid
      if (data.repetition_indicator === undefined) {
        data.repetition_indicator = false
      }
      if (!this.diseaseMilestone) {
        study.createStudyDiseaseMilestone(this.selectedStudy.uid, data).then(resp => {
          this.$refs.form.working = false
          bus.$emit('notification', { msg: this.$t('DiseaseMilestoneForm.add_success') })
          this.close()
        }, _err => {
          this.$refs.form.working = false
        })
      } else {
        study.updateStudyDiseaseMilestone(this.selectedStudy.uid, this.diseaseMilestone.uid, data).then(resp => {
          this.$refs.form.working = false
          bus.$emit('notification', { msg: this.$t('DiseaseMilestoneForm.update_success') })
          this.close()
        }, _err => {
          this.$refs.form.working = false
        })
      }
    }
  },
  mounted () {
    terms.getByCodelist('diseaseMilestoneTypes').then(resp => {
      this.diseaseMilestoneTypes = resp.data.items
    })
  },
  watch: {
    diseaseMilestone: {
      handler: function (newValue) {
        if (newValue) {
          this.form = { ...newValue }
        } else {
          this.form = {}
        }
      },
      immediate: true
    }
  }
}
</script>
