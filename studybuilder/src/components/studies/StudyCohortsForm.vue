<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="cancel"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <validation-provider
        v-slot="{ errors }"
        >
        <v-row>
          <v-col cols="12">
            <v-autocomplete
              v-model="form.arm_uids"
              :label="$t('StudyCohorts.study_arm')"
              data-cy="study-arm"
              :items="arms"
              item-text="name"
              item-value="arm_uid"
              :error-messages="errors"
              clearable
              multiple
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        >
        <v-row>
          <v-col cols="12">
            <v-autocomplete
              v-model="form.branch_arm_uids"
              :label="$t('StudyCohorts.study_branch_arm')"
              data-cy="branch-arm"
              :items="branches"
              item-text="name"
              item-value="branch_arm_uid"
              :error-messages="errors"
              clearable
              multiple
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required|max:200"
        >
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.name"
              :label="$t('StudyCohorts.cohort_name')"
              data-cy="study-cohort-name"
              :error-messages="errors"
              clearable
              class="required"
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required|max:20"
        >
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.short_name"
              :label="$t('StudyCohorts.cohort_short_name')"
              data-cy="study-cohort-short-name"
              :error-messages="errors"
              clearable
              class="required"
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required|max:20"
        >
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.code"
              :label="$t('StudyCohorts.cohort_code')"
              data-cy="study-cohort-code"
              :error-messages="errors"
              clearable
              class="required"
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        :rules="`min_value:1|max_value:${findMaxNuberOfSubjects()}`"
        >
        <v-row>
          <v-col cols="12">
            <v-text-field
              :disabled="!form.arm_uids"
              :value="form.number_of_subjects"
              @input="form.number_of_subjects = $event !== '' ? $event : null"
              :label="$t('StudyCohorts.nuber_of_subjects')"
              data-cy="study-cohort-planned-number-of-subjects"
              :error-messages="(errors[0] && errors[0].includes($t('StudyCohorts.value_less_then'))) ? $t('StudyCohorts.number_of_subjects_exceeds') : errors"
              type="number"
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        >
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="form.description"
              :label="$t('_global.description')"
              data-cy="study-cohort-description"
              :error-messages="errors"
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <div class="mt-4">
        <label class="v-label">{{ $t('StudyCohorts.colour') }}</label>
        <v-color-picker
          v-model="colorHash"
          clearable
          show-swatches
          hide-canvas
          hide-sliders
          swatches-max-height="300px"
          />
      </div>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>

import { mapGetters } from 'vuex'
import arms from '@/api/arms'
import { bus } from '@/main'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import _isEqual from 'lodash/isEqual'

export default {
  components: {
    SimpleFormDialog
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    }),
    title () {
      return (Object.keys(this.editedCohort).length !== 0)
        ? this.$t('StudyCohorts.edit_cohort')
        : this.$t('StudyCohorts.add_cohort')
    }
  },
  props: {
    editedCohort: Object,
    arms: Array,
    branches: Array,
    open: Boolean
  },
  data () {
    return {
      form: {},
      helpItems: [],
      colorHash: null
    }
  },
  methods: {
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      if (Object.keys(this.editedCohort).length !== 0) {
        this.edit()
      } else {
        this.create()
      }
    },
    async create () {
      if (this.colorHash) {
        this.form.colour_code = this.colorHash.hexa
      }
      arms.createCohort(this.selectedStudy.uid, this.form).then(resp => {
        bus.$emit('notification', { msg: this.$t('StudyCohorts.cohort_created') })
        this.close()
      })
    },
    edit () {
      if (this.colorHash) {
        this.form.colour_code = this.colorHash.hexa !== undefined ? this.colorHash.hexa : this.colorHash
      }
      arms.editCohort(this.selectedStudy.uid, this.editedCohort.cohort_uid, this.form).then(resp => {
        bus.$emit('notification', { msg: this.$t('StudyCohorts.cohort_updated') })
        this.close()
      })
    },
    close () {
      this.form = {}
      this.$store.commit('form/CLEAR_FORM')
      this.colorHash = null
      this.$refs.observer.reset()
      this.$emit('close')
    },
    async cancel () {
      if (this.$store.getters['form/form'] === '' || _isEqual(this.$store.getters['form/form'], JSON.stringify(this.form))) {
        this.close()
      } else {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue')
        }
        if (await this.$refs.form.confirm(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      }
    },
    findMaxNuberOfSubjects () {
      let subjectsSum = 0
      if (this.form.arm_uids) {
        this.form.arm_uids.forEach(el => {
          subjectsSum += this.arms.find(e => e.arm_uid === el).number_of_subjects
        })
      }
      return subjectsSum
    }
  },
  mounted () {
    if (Object.keys(this.editedCohort).length !== 0) {
      this.form = JSON.parse(JSON.stringify(this.editedCohort))
      this.$set(this.form, 'arm_uids', this.editedCohort.arm_roots ? this.editedCohort.arm_roots.map(el => el.arm_uid) : null)
      this.$set(this.form, 'branch_arm_uids', this.editedCohort.branch_arm_roots ? this.editedCohort.branch_arm_roots.map(el => el.branch_arm_uid) : null)
      if (this.editedCohort.colour_code) {
        this.colorHash = this.editedCohort.colour_code
      }
      this.$store.commit('form/SET_FORM', this.form)
    }
  },
  watch: {
    editedCohort (value) {
      if (Object.keys(value).length !== 0) {
        this.form = JSON.parse(JSON.stringify(value))
        this.$set(this.form, 'arm_uids', value.arm_roots ? value.arm_roots.map(el => el.arm_uid) : null)
        this.$set(this.form, 'branch_arm_uids', value.branch_arm_roots ? value.branch_arm_roots.map(el => el.branch_arm_uid) : null)
        if (value.colour_code) {
          this.colorHash = value.colour_code
        }
        this.$store.commit('form/SET_FORM', this.form)
      }
    }
  }
}
</script>
