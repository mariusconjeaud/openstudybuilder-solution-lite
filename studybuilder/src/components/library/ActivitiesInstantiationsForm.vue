<template>
<v-card>
  <stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="cancel"
    @save="submit"
    :form-observer-getter="getObserver"
    :help-items="helpItems"
    >
    <template v-slot:step.type="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
              <v-select
                v-model="form.activity_instance_class_uid"
                :items="activityInstanceClasses"
                :label="$t('ActivityForms.type')"
                item-text="name"
                item-value="uid"
                dense
                clearable
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
            <v-col>
              <v-text-field
                v-model="form.name"
                :label="$t('ActivityForms.name')"
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
            <v-col>
              <v-autocomplete
                v-model="form.activity_groupings[0].activity_uid"
                :items="activities"
                :label="$t('ActivityForms.activity')"
                item-text="name"
                item-value="uid"
                dense
                clearable
                :error-messages="errors"
                class="pt-3"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              :items="filteredGroups"
              v-model="form.activity_groupings[0].activity_group_uid"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
              :disabled="form.activity_groupings[0].activity_uid ? false : true"
              />
          </v-col>
        </v-row>
      </validation-provider>
        <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_subgroup')"
              :items="filteredSubGroups"
              v-model="form.activity_groupings[0].activity_subgroup_uid"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
              :disabled="form.activity_groupings[0].activity_group_uid ? false : true"
              />
          </v-col>
        </v-row>
      </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
              <v-textarea
                v-model="form.definition"
                :label="$t('ActivityForms.definition')"
                hide-details
                class="mb-4"
                :error-messages="errors"
                auto-grow
                rows="1"
              />
            </v-col>
          </v-row>
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
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
            <v-col>
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
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          >
          <v-row>
            <v-col>
              <v-text-field
                v-model="form.legacy_description"
                :label="$t('ActivityForms.legacyDesc')"
                hide-details
                class="mb-4"
                :error-messages="errors"
              />
            </v-col>
          </v-row>
        </validation-provider>
      </validation-observer>
    </template>
  </stepper-form>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</v-card>
</template>

<script>
import _isEmpty from 'lodash/isEmpty'
import _isEqual from 'lodash/isEqual'
import activityInstanceClasses from '@/api/activityInstanceClasses'
import activities from '@/api/activities'
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import libraries from '@/constants/libraries'
import StepperForm from '@/components/tools/StepperForm'

const source = 'activity-instances'

export default {
  components: {
    ConfirmDialog,
    StepperForm
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
      form: {
        activity_groupings: [{}]
      },
      type: '',
      activities: [],
      activityInstanceClasses: [],
      steps: this.getInitialSteps(),
      helpItems: [
        'ActivityFormsInstantiations.select_type',
        'ActivityFormsInstantiations.name',
        'ActivityFormsInstantiations.definition',
        'ActivityFormsInstantiations.activities',
        'ActivityFormsInstantiations.topicCode',
        'ActivityFormsInstantiations.adamCode',
        'ActivityFormsInstantiations.legacyDesc'
      ]
    }
  },
  methods: {
    initForm (value) {
      this.form = {
        name: value.name,
        activity_instance_class_uid: value.activity_instance_class.uid,
        name_sentence_case: value.name_sentence_case,
        definition: value.definition,
        change_description: value.change_description,
        activity_sub_groups: value.activity_sub_groups,
        topic_code: value.topic_code,
        adam_param_code: value.adam_param_code,
        legacy_description: value.legacy_description,
        activity_groupings: [{}]
      }
      if (!_isEmpty(value)) {
        const grouping = [{}]
        if (value.activities) {
          grouping[0].activity_name = value.activities[0].name
          grouping[0].activity_uid = value.activities[0].uid
        }
        if (value.activity_group) {
          grouping[0].activity_group_name = value.activity_group.name
          grouping[0].activity_group_uid = value.activity_group.uid
        }
        if (value.activity_subgroup) {
          grouping[0].activity_subgroup_name = value.activity_subgroup.name
          grouping[0].activity_subgroup_uid = value.activity_subgroup.uid
        }
        this.$set(this.form, 'activity_groupings', grouping)
      } else {
        const grouping = [{}]
        this.$set(this.form, 'activity_groupings', grouping)
      }
      this.$store.commit('form/SET_FORM', this.form)
    },
    getInitialSteps () {
      return [
        { name: 'type', title: this.$t('ActivityForms.select_type') },
        { name: 'basicData', title: this.$t('ActivityForms.addBasicData') }
      ]
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
      this.form = { activity_groupings: [{}] }
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.stepper.reset()
      this.$refs.stepper.loading = false
    },
    async submit () {
      this.form.library_name = libraries.LIBRARY_SPONSOR
      this.form.name_sentence_case = this.form.name.charAt(0).toUpperCase() + this.form.name.slice(1)
      this.form.activities = [this.form.activities]
      if (!this.editedActivity) {
        activities.create(this.form, source).then(() => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_created') })
          this.close()
        })
      } else {
        activities.update(this.editedActivity.uid, this.form, source).then(() => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_updated') })
          this.close()
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
    editedActivity: {
      handler (value) {
        if (value) {
          this.initForm(value)
        }
      },
      immediate: true
    }
  }
}
</script>
