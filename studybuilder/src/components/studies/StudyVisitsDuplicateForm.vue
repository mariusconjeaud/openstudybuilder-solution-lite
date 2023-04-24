<template>
<simple-form-dialog
  ref="form"
  :title="$t('StudyVisitForm.duplicate_visit')"
  @close="close"
  @submit="submit"
  :open="open"
  max-width="400px"
  :help-items="helpItems"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-text-field
          :label="$t('StudyVisitForm.time_value')"
          dense
          v-model="form.timing"
          :error-messages="errors"
          type="number"
        />
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-autocomplete
          v-model="form.time_unit_uid"
          :label="$t('StudyVisitForm.time_unit_name')"
          data-cy="time-unit"
          :items="timeUnits"
          item-text="name"
          item-value="uid"
          :error-messages="errors"
          clearable
          />
      </validation-provider>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import { mapGetters } from 'vuex'
import { bus } from '@/main'
import epochs from '@/api/studyEpochs'
import unitConstants from '@/constants/units'
import units from '@/api/units'

export default {
  components: {
    SimpleFormDialog
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  props: {
    studyVisit: Object,
    open: Boolean
  },
  data () {
    return {
      timeUnits: [],
      form: {},
      helpItems: [
        'StudyVisitDuplicate.time_value',
        'StudyVisitDuplicate.time_unit'
      ]
    }
  },
  methods: {
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      try {
        this.$refs.form.working = true
        const newVisit = structuredClone(this.studyVisit)
        newVisit.time_value = this.form.timing
        newVisit.time_unit_uid = this.form.time_unit_uid
        await epochs.getStudyVisitPreview(this.selectedStudy.uid, newVisit).then(resp => {
          for (const field of ['visit_name', 'visit_short_name', 'study_day_label', 'study_week_label', 'study_day_number', 'study_week_number', 'duration_time', 'unique_visit_number', 'visit_number']) {
            this.$set(newVisit, field, resp.data[field])
          }
          this.$store.dispatch('studyEpochs/addStudyVisit', { studyUid: this.selectedStudy.uid, input: newVisit }).then(resp => {
            this.$store.dispatch('studyEpochs/fetchStudyVisits', this.selectedStudy.uid)
          })
          bus.$emit('notification', { msg: this.$t('StudyVisitForm.visit_duplicated') })
          this.close()
        })
      } finally {
        this.$refs.form.working = false
      }
    },
    close () {
      this.form = {}
      this.$refs.observer.reset()
      this.$emit('close')
    }
  },
  mounted () {
    units.getBySubset(unitConstants.TIME_UNIT_SUBSET_STUDY_TIME).then(resp => {
      this.timeUnits = resp.data.items
    })
  },
  watch: {
    studyVisit: {
      handler: function (newVal) {
        if (newVal) {
          this.$set(this.form, 'time_unit_uid', newVal.time_unit_uid)
        }
      },
      immediate: true
    }
  }
}
</script>
