<template>
<v-card>
  <horizontal-stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="cancel"
    @save="submit"
    :form-observer-getter="getObserver"
    :help-items="helpItems"
    :extra-step-validation="extraValidation"
    >
    <template v-slot:step.activities="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="4">
              <v-autocomplete
                v-model="selectedActivity"
                :items="activities"
                :label="$t('ActivityForms.activity')"
                item-text="name"
                dense
                clearable
                :error-messages="errors"
                class="mt-4"
                return-object
                @change="selectedGroupings = []"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <validation-provider>
          <v-row>
            <v-col>
              <v-data-table
                v-if="selectedActivity"
                class="mb-3 pb-3"
                hide-default-footer
                show-select
                v-model="selectedGroupings"
                :headers="headers"
                item-key="activity_subgroup_uid"
                :items="selectedActivity.activity_groupings"/>
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
    <v-spacer/>
    </template>
    <template v-slot:step.type="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="4">
              <v-select
                v-model="form.activity_instance_class_uid"
                :items="activityInstanceClasses"
                :label="$t('ActivityForms.instance_class')"
                item-text="name"
                item-value="uid"
                dense
                clearable
                class="mt-4"
                :error-messages="errors"
              />
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
    </template>
    <template v-slot:step.basicData="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="8">
              <v-text-field
                v-model="form.name"
                :label="$t('ActivityForms.activity_ins_name')"
                hide-details
                class="mb-4"
                :error-messages="errors"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <v-row>
          <v-col cols="8">
            <sentence-case-name-field
              :name="form.name"
              :initial-name="form.name_sentence_case"
              v-model="form.name_sentence_case"/>
          </v-col>
        </v-row>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="8">
              <v-textarea
                v-model="form.definition"
                :label="$t('ActivityForms.definition')"
                hide-details
                class="mb-4"
                :error-messages="errors"
                auto-grow
                rows="2"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <v-row>
          <v-col cols="8">
            <v-text-field
              :label="$t('ActivityTable.nci_concept_id')"
              v-model="form.nci_concept_id"
              dense
              clearable
              />
          </v-col>
        </v-row>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="8">
              <v-text-field
                v-model="form.topic_code"
                :label="$t('ActivityForms.topicCode')"
                hide-details
                class="mb-4"
                :error-messages="errors"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col cols="8">
              <v-text-field
                v-model="form.adam_param_code"
                :label="$t('ActivityForms.adamCode')"
                hide-details
                class="mb-4"
                :error-messages="errors"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <v-row>
          <v-col>
            <v-checkbox
              :label="$t('ActivityForms.is_required_for_activity')"
              v-model="form.is_required_for_activity">
            </v-checkbox>
            <v-checkbox
              :label="$t('ActivityForms.is_default_selected_for_activity')"
              v-model="form.is_default_selected_for_activity">
            </v-checkbox>
          </v-col>
          <v-col>
            <v-checkbox
              :label="$t('ActivityForms.is_data_sharing')"
              v-model="form.is_data_sharing">
            </v-checkbox>
            <v-checkbox
              :label="$t('ActivityForms.is_legacy_usage')"
              v-model="form.is_legacy_usage">
            </v-checkbox>
          </v-col>
        </v-row>
      </validation-observer>
    </template>
  </horizontal-stepper-form>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</v-card>
</template>

<script>
import _isEqual from 'lodash/isEqual'
import activityInstanceClasses from '@/api/activityInstanceClasses'
import activities from '@/api/activities'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import libraries from '@/constants/libraries'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm'
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField'

const source = 'activity-instances'

export default {
  components: {
    ConfirmDialog,
    HorizontalStepperForm,
    SentenceCaseNameField
  },
  props: {
    editedActivity: Object
  },
  computed: {
    title () {
      return (this.editedActivity)
        ? this.$t('ActivityForms.editInstance')
        : this.$t('ActivityForms.addInstance')
    },
    filteredGroups () {
      if (!this.form.activity_groupings || !this.form.activity_groupings[0].activity_uid) {
        return []
      }
      const uid = this.form.activity_groupings[0].activity_uid
      const activity = this.activities.find(o => o.uid === uid)
      if (!activity) {
        return []
      }
      return activity.activity_groupings.map((o) => ({ name: o.activity_group_name, uid: o.activity_group_uid }))
    },
    filteredSubGroups () {
      if (!this.form.activity_groupings || !this.form.activity_groupings[0].activity_group_uid) {
        return []
      }
      const activityUid = this.form.activity_groupings[0].activity_uid
      const groupUid = this.form.activity_groupings[0].activity_group_uid
      const activity = this.activities.find(o => o.uid === activityUid)
      if (!activity) {
        return []
      }
      return activity.activity_groupings.filter(o => o.activity_group_uid === groupUid).map((o) => ({ name: o.activity_subgroup_name, uid: o.activity_subgroup_uid }))
    }
  },
  data () {
    return {
      form: { activity_groupings: [] },
      type: '',
      activities: [],
      activityInstanceClasses: [],
      steps: this.getInitialSteps(),
      helpItems: [
        'ActivityFormsInstantiations.activities',
        'ActivityFormsInstantiations.activity_group',
        'ActivityFormsInstantiations.select_type',
        'ActivityFormsInstantiations.name',
        'ActivityFormsInstantiations.definition',
        'ActivityFormsInstantiations.nci_concept_id',
        'ActivityFormsInstantiations.topicCode',
        'ActivityFormsInstantiations.adamCode',
        'ActivityFormsInstantiations.is_required_for_activity',
        'ActivityFormsInstantiations.is_default_selected_for_activity',
        'ActivityFormsInstantiations.is_data_sharing',
        'ActivityFormsInstantiations.is_legacy_usage'
      ],
      headers: [
        { text: this.$t('ActivityFormsInstantiations.activity_group'), value: 'activity_group_name' },
        { text: this.$t('ActivityFormsInstantiations.activity_subgroup'), value: 'activity_subgroup_name' }
      ],
      selectedActivity: null,
      selectedGroupings: []
    }
  },
  methods: {
    initForm (value) {
      this.form = {
        name: value.name,
        activity_instance_class_uid: value.activity_instance_class.uid,
        name_sentence_case: value.name_sentence_case,
        nci_concept_id: value.nci_concept_id,
        definition: value.definition,
        change_description: value.change_description,
        activity_sub_groups: value.activity_sub_groups,
        topic_code: value.topic_code,
        adam_param_code: value.adam_param_code,
        is_required_for_activity: value.is_required_for_activity,
        is_default_selected_for_activity: value.is_default_selected_for_activity,
        is_data_sharing: value.is_data_sharing,
        is_legacy_usage: value.is_legacy_usage,
        activity_groupings: []
      }
      this.$store.commit('form/SET_FORM', this.form)
    },
    getInitialSteps () {
      return [
        { name: 'activities', title: this.$t('ActivityForms.select_activities') },
        { name: 'type', title: this.$t('ActivityForms.select_class') },
        { name: 'basicData', title: this.$t('ActivityForms.addBasicData') }
      ]
    },
    async extraValidation (step) {
      if (step !== 1) {
        return true
      }
      if (this.selectedGroupings.length === 0) {
        bus.$emit('notification', { msg: this.$t('ActivityForms.grouping_selection_info'), type: 'info' })
        return false
      }
      return true
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
        if (await this.$refs.confirm.open(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      }
    },
    close () {
      this.$emit('close')
      this.form = { activity_groupings: [] }
      this.selectedActivity = null
      this.selectedGroupings = []
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.stepper.reset()
      this.$refs.stepper.loading = false
    },
    async submit () {
      this.form.library_name = libraries.LIBRARY_SPONSOR
      this.form.activities = [this.form.activities]
      this.selectedGroupings.forEach(grouping => {
        this.form.activity_groupings.push({ activity_uid: this.selectedActivity.uid, activity_group_uid: grouping.activity_group_uid, activity_subgroup_uid: grouping.activity_subgroup_uid })
      })
      if (!this.editedActivity) {
        activities.create(this.form, source).then(() => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_created') })
          this.close()
        }, () => {
          this.$refs.stepper.loading = false
        })
      } else {
        activities.update(this.editedActivity.uid, this.form, source).then(() => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_updated') })
          this.close()
        }, () => {
          this.$refs.stepper.loading = false
        })
      }
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    getActivities () {
      activities.get({ page_size: 0 }, 'activities').then(resp => {
        this.activities = resp.data.items
      })
    },
    setActivityGroupings () {
      this.selectedActivity = this.activities.find(act => act.uid === this.editedActivity.activities[0].uid)
      if (this.editedActivity.activity_groupings.length > 0) {
        this.selectedGroupings = []
        this.editedActivity.activity_groupings.forEach(grouping => {
          this.selectedGroupings.push(this.selectedActivity.activity_groupings.find(group => (group.activity_group_uid === grouping.activity_group.uid && group.activity_subgroup_uid === grouping.activity_subgroup.uid)))
        })
      }
    }
  },
  mounted () {
    if (this.editedActivity) {
      this.initForm(this.editedActivity)
    }
    this.getActivities()
    activityInstanceClasses.getAll({ page_size: 0 }).then(resp => {
      this.activityInstanceClasses = resp.data.items
    })
  },
  watch: {
    activities (value) {
      if (this.editedActivity) {
        this.setActivityGroupings()
      }
    },
    editedActivity: {
      handler (value) {
        if (value) {
          this.initForm(value)
        }
        if (this.editedActivity && this.activities.length > 0) {
          this.setActivityGroupings()
        }
      },
      immediate: true
    }
  }
}
</script>
