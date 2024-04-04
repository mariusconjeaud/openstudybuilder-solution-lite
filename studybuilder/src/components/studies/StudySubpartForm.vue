<template>
<v-card>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="cancel"
    @save="submit"
    :form-observer-getter="getObserver"
    :extra-step-validation="extraValidation"
    >
    <template v-slot:step.method>
      <v-radio-group
        v-model="method">
        <v-radio :label="$t('StudySubparts.add_existing')" value="select" />
        <v-radio :label="$t('StudySubparts.create_new')" value="create" />
      </v-radio-group>
    </template>
    <template v-slot:step.select="{ step }">
      <validation-observer :ref="`observer_${step}`">
      <v-card class="px-4 mb-2">
        <v-card-title class="dialog-title">
          {{ $t('StudySubparts.selected_substudy') }}
        </v-card-title>
        <v-card-text>
          <v-data-table
            key="uid"
            :headers="selectedHeaders"
            :items="[selectedSubstudy]"
            hide-default-footer
            >
          </v-data-table>
        </v-card-text>
      </v-card>
      <v-card class="px-4 mb-2">
        <v-card-title class="dialog-title">
          {{ $t('StudySubparts.available_studies') }}
        </v-card-title>
        <v-card-text>
          <n-n-table
            key="uid"
            :headers="headers"
            :items="studies"
            has-api
            :server-items-length="total"
            :options.sync="options"
            @filter="fetchAvailableStudies"
            column-data-resource="studies"
            >
            <template v-slot:item.select="{ item }">
              <v-btn
                icon
                @click="selectStudy(item)"
                :title="$t('StudySelectionTable.copy_item')">
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
          </template>
          </n-n-table>
        </v-card-text>
      </v-card>
      </validation-observer>
    </template>
    <template v-slot:step.create="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-row>
          <v-col cols="8">
              <v-text-field
                :label="$t('StudyForm.project_id')"
                :value="selectedStudy.current_metadata.identification_metadata.project_number"
                disabled
                filled
                hide-details
                data-cy="project-name"
                />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <v-text-field
              :label="$t('StudyForm.project_name')"
              :value="selectedStudy.current_metadata.identification_metadata.project_name"
              disabled
              filled
              hide-details
              ></v-text-field>
          </v-col>
        </v-row>
        <!-- Brand name is not yet implemented in api -->
        <v-row>
          <v-col cols="8">
            <v-text-field
              :label="$t('StudyForm.brand_name')"
              disabled
              filled
              hide-details
              ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8">
            <v-text-field
              :label="$t('StudyForm.acronym')"
              v-model="form.study_acronym"
              dense
              clearable
              ></v-text-field>
          </v-col>
        </v-row>
      </validation-observer>
    </template>
    <template v-slot:step.define="{ step }">
      <validation-observer :ref="`observer_${step}`">
      <v-card class="px-4 mb-2" v-if="method === 'select' && checkIfEdit()">
        <v-card-title class="dialog-title">
          {{ $t('StudySubparts.selected_substudy') }}
        </v-card-title>
        <v-card-text>
          <v-data-table
            key="uid"
            :headers="selectedHeaders"
            :items="[selectedSubstudy]"
            hide-default-footer
            >
          </v-data-table>
        </v-card-text>
      </v-card>
      <v-card class="px-4">
        <v-card-title class="dialog-title">
          {{ $t('StudySubparts.subpart_attrs') }}
        </v-card-title>
        <v-card-text>
        <v-row>
          <v-col cols="3" class="dialog-title text-h6">
          {{ $t('StudySubparts.derived_subpart_id') }}
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="form.study_number"
              dense
              disabled
              filled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="3" class="dialog-title text-h6">
          {{ $t('StudySubparts.study_subpart_acronym') }}
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="form.study_acronym"
              dense
              :disabled="Object.entries(editedSubpart).length === 0"
              filled
              hide-details
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="8" class="dialog-title text-h6">
            {{ $t('_global.description') }}
            <v-textarea
              v-model="form.description"
              dense
              clearable
              auto-grow
              rows="3"
              />
          </v-col>
        </v-row>
        </v-card-text>
      </v-card>
      </validation-observer>
    </template>
  </horizontal-stepper-form>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</v-card>
</template>

<script>
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import { mapGetters } from 'vuex'
import studies from '@/api/study'
import _isEmpty from 'lodash/isEmpty'
import filteringParameters from '@/utils/filteringParameters'
import NNTable from '@/components/tools/NNTable'

export default {
  components: {
    ConfirmDialog,
    HorizontalStepperForm,
    NNTable
  },
  props: {
    editedSubpart: Object
  },
  computed: {
    title () {
      return (!_isEmpty(this.editedSubpart))
        ? this.$t('StudySubparts.edit_subpart')
        : this.$t('StudySubparts.add_subpart')
    },
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      form: {},
      steps: this.getInitialSteps(),
      selectSteps: [
        { name: 'method', title: this.$t('StudySubparts.select_method') },
        { name: 'select', title: this.$t('StudySubparts.select_study_subpart') },
        { name: 'define', title: this.$t('StudySubparts.define_subpart') }
      ],
      createSteps: [
        { name: 'method', title: this.$t('StudySubparts.select_method') },
        { name: 'create', title: this.$t('StudySubparts.create_subpart') },
        { name: 'define', title: this.$t('StudySubparts.define_subpart') }
      ],
      method: 'select',
      headers: [
        { text: '', value: 'select', width: '5%' },
        { text: this.$t('StudyTable.acronym'), value: 'current_metadata.identification_metadata.study_acronym' },
        { text: this.$t('StudyTable.title'), value: 'current_metadata.study_description.study_title' },
        { text: this.$t('_global.description'), value: 'current_metadata.identification_metadata.description' }
      ],
      selectedHeaders: [
        { text: this.$t('StudyTable.acronym'), value: 'current_metadata.identification_metadata.study_acronym' },
        { text: this.$t('StudyTable.title'), value: 'current_metadata.study_description.study_title' },
        { text: this.$t('_global.description'), value: 'current_metadata.identification_metadata.description' }
      ],
      studies: [],
      selectedSubstudy: {},
      options: {},
      total: 0
    }
  },
  mounted () {
    this.initForm()
    this.fetchAvailableStudies()
  },
  methods: {
    checkIfEdit () {
      return _isEmpty(this.editedSubpart)
    },
    initForm () {
      this.form = {}
      if (!_isEmpty(this.editedSubpart)) {
        this.selectedSubstudy = this.editedSubpart
        this.form.study_number = this.editedSubpart.current_metadata.identification_metadata.study_number
        this.form.study_acronym = this.editedSubpart.current_metadata.identification_metadata.study_acronym
        this.form.description = this.editedSubpart.current_metadata.identification_metadata.description
      }
      this.$store.commit('form/SET_FORM', this.form)
    },
    selectStudy (study) {
      this.selectedSubstudy = study
      this.form.description = study.current_metadata.identification_metadata.description
      this.form.study_acronym = study.current_metadata.identification_metadata.study_acronym
    },
    fetchAvailableStudies (filters, sort, filtersUpdated) {
      if (filters) {
        const filtersObj = JSON.parse(filters)
        filtersObj.study_subpart_uids = { v: [] }
        filtersObj.study_parent_part = { v: [] }
        filtersObj.uid = { v: [this.selectedStudy.uid], op: 'ne' }
        filters = JSON.stringify(filtersObj)
      } else {
        filters = { uid: { v: [this.selectedStudy.uid], op: 'ne' }, study_subpart_uids: { v: [] }, study_parent_part: { v: [] } }
      }
      const params = filteringParameters.prepareParameters(
        this.options, filters, sort, filtersUpdated)
      studies.get(params).then(resp => {
        this.studies = resp.data.items
        this.total = resp.data.total
      })
    },
    async extraValidation (step) {
      if (step !== 2) {
        return true
      }
      if (this.method === 'select' && _isEmpty(this.selectedSubstudy)) {
        bus.$emit('notification', { msg: this.$t('StudySubparts.select_study_warning'), type: 'info' })
        return false
      }
      return true
    },
    async cancel () {
      this.close()
    },
    close () {
      this.$emit('close')
      this.method = 'select'
      this.steps = this.selectSteps
      this.form = {}
      this.selectedSubstudy = {}
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.stepper.reset()
      this.$refs.stepper.loading = false
    },
    submit () {
      if (!_isEmpty(this.editedSubpart)) {
        this.selectedSubstudy.study_parent_part_uid = this.selectedStudy.uid
        this.selectedSubstudy.current_metadata.identification_metadata.description = this.form.description
        this.selectedSubstudy.current_metadata.identification_metadata.study_acronym = this.form.study_acronym
        delete this.selectedSubstudy.current_metadata.study_description
        delete this.selectedSubstudy.study_parent_part
        studies.updateStudy(this.selectedSubstudy.uid, this.selectedSubstudy).then(() => {
          bus.$emit('notification', { msg: this.$t('StudySubparts.subpart_created') })
          this.$refs.stepper.loading = false
          this.close()
        })
      } else if (this.method === 'select') {
        this.selectedSubstudy.study_parent_part_uid = this.selectedStudy.uid
        this.selectedSubstudy.current_metadata.identification_metadata.description = this.form.description
        studies.updateStudy(this.selectedSubstudy.uid, this.selectedSubstudy).then(() => {
          bus.$emit('notification', { msg: this.$t('StudySubparts.subpart_created') })
          this.$refs.stepper.loading = false
          this.close()
        })
      } else {
        this.form.project_number = this.selectedStudy.current_metadata.identification_metadata.project_number
        this.form.study_parent_part_uid = this.selectedStudy.uid
        this.$store.dispatch('manageStudies/addStudy', this.form).then(() => {
          bus.$emit('notification', { msg: 'Study subpart created' })
          this.close()
        })
      }
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    getInitialSteps () {
      if (!_isEmpty(this.editedSubpart)) {
        return [
          { name: 'define', title: this.$t('StudySubparts.define_subpart') }
        ]
      }
      return [
        { name: 'method', title: this.$t('StudySubparts.select_method') },
        { name: 'select', title: this.$t('StudySubparts.select_study_subpart') },
        { name: 'define', title: this.$t('StudySubparts.define_subpart') }
      ]
    }
  },
  watch: {
    method (value) {
      this.steps = value === 'select' ? this.selectSteps : this.createSteps
      this.form = {}
    },
    editedSubpart (value) {
      if (!_isEmpty(value)) {
        this.steps = [{ name: 'define', title: this.$t('StudySubparts.define_subpart') }]
        this.initForm()
      }
    }
  }
}
</script>
