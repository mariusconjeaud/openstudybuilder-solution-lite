<template>
<v-card>
  <stepper-form
    ref="stepper"
    :title="title"
    :steps="steps"
    @close="close"
    @save="submit"
    :form-observer-getter="getObserver"
    :help-items="helpItems"
    >
    <template v-slot:step.request="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              data-cy="handlerequestform-activity-group-dropdown"
              :items="groups"
              v-model="activity.activity_groupings[0].activity_group_uid"
              item-text="name"
              item-value="uid"
              dense
              readonly
              ></v-autocomplete>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_subgroup')"
              data-cy="handlerequestform-activity-subgroup-dropdown"
              :items="subGroups"
              v-model="activity.activity_groupings[0].activity_subgroup_uid"
              item-text="name"
              item-value="uid"
              dense
              readonly
              ></v-autocomplete>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              :label="$t('ActivityForms.activity_name')"
              data-cy="handlerequestform-activity-name-field"
              v-model="activity.name"
              dense
              clearable
              readonly
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              :label="$t('ActivityFormsRequested.abbreviation')"
              data-cy="handlerequestform-abbreviation-field"
              v-model="activity.abbreviation"
              dense
              clearable
              readonly
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-textarea
              :label="$t('ActivityFormsRequested.definition')"
              data-cy="handlerequestform-definition-field"
              v-model="activity.definition"
              dense
              clearable
              auto-grow
              rows="1"
              readonly
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-textarea
              :label="$t('ActivityFormsRequested.rationale_for_request')"
              data-cy="handlerequestform-rationale-for-request-field"
              v-model="activity.request_rationale"
              dense
              clearable
              auto-grow
              rows="1"
              readonly
              />
          </v-col>
        </v-row>
      </validation-observer>
    </template>
    <template v-slot:step.sponsor="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-autocomplete
                :label="$t('ActivityForms.activity_group')"
                data-cy="sponsorform-activity-group-dropdown"
                :items="groups"
                v-model="form.activity_groupings[0].activity_group_uid"
                item-text="name"
                item-value="uid"
                dense
                clearable
                :error-messages="errors"
                @change="filterSubGroups"
                />
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-autocomplete
                :label="$t('ActivityForms.activity_subgroup')"
                data-cy="sponsorform-activity-subgroup-dropdown"
                :items="filteredSubGroups"
                v-model="subgroup"
                item-text="name"
                item-value="uid"
                dense
                clearable
                :disabled="form.activity_groupings[0].activity_group_uid ? false : true"
                :error-messages="errors"
                return-object
                />
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-text-field
                :label="$t('ActivityForms.activity_name')"
                data-cy="sponsorform-activity-name-field"
                v-model="form.name"
                dense
                clearable
                @input="getActivities"
                :error-messages="errors"
                />
            </validation-provider>
            <sentence-case-name-field
              :name="form.name"
              :initial-name="form.name_sentence_case"
              v-model="form.name_sentence_case"/>
            <v-row>
              <v-col>
                <v-text-field
                  :label="$t('ActivityForms.nci_concept_id')"
                  data-cy="sponsorform-nciconceptid-field"
                  v-model="form.nci_concept_id"
                  dense
                  clearable
                  />
              </v-col>
            </v-row>
            <v-text-field
              :label="$t('ActivityFormsRequested.abbreviation')"
              data-cy="sponsorform-abbreviation-field"
              v-model="form.abbreviation"
              dense
              clearable
              />
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-textarea
                :label="$t('ActivityFormsRequested.definition')"
                data-cy="sponsorform-definition-field"
                v-model="form.definition"
                dense
                clearable
                auto-grow
                rows="1"
                :error-messages="errors"
                />
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-textarea
                :label="$t('ActivityFormsRequested.rationale_for_request')"
                data-cy="sponsorform-rationale-for-request-field"
                v-model="form.request_rationale"
                dense
                clearable
                auto-grow
                rows="1"
                :error-messages="errors"
                />
              </validation-provider>
              <v-row>
                <v-col>
                  <v-checkbox
                    :label="$t('ActivityForms.is_data_collected')"
                    data-cy="sponsorform-datacollected-checkbox"
                    v-model="form.is_data_collected">
                  </v-checkbox>
                </v-col>
              </v-row>
          </v-col>
        </v-row>
      </validation-observer>
    </template>
    <template v-slot:step.confirm="{ step }">
      <validation-observer :ref="`observer_${step}`">
        <v-row>
          <v-col cols="6">
            <div class="text-h5 mb-8">{{ $t('ActivityFormsRequested.requested_activity') }}</div>
            <v-text-field
              :label="$t('ActivityForms.activity_group')"
              data-cy="confirmation-request-group-field"
              v-model="activity.activity_groupings[0].activity_group_name"
              dense
              readonly
              v-if="activity.activity_group"
              />
            <v-text-field
              :label="$t('ActivityForms.activity_subgroup')"
              data-cy="confirmation-request-subgroup-field"
              v-model="activity.activity_groupings[0].activity_subgroup_name"
              dense
              readonly
              v-if="activity.activity_groupings[0].activity_group_uid ? false : true"
              />
            <v-text-field
              :label="$t('ActivityForms.activity_name')"
              data-cy="confirmation-request-activity-name-field"
              v-model="activity.name"
              dense
              readonly
              />
          </v-col>
          <v-col cols="6">
            <div class="text-h5 mb-8">{{ $t('ActivityFormsRequested.new_sponsor_concept')  }}</div>
            <v-text-field
              :label="$t('ActivityForms.activity_group')"
              data-cy="confirmation-sponsor-group-field"
              v-model="form.activity_groupings[0].activity_group_name"
              dense
              readonly
              v-if="activity.activity_groupings[0].activity_group_uid ? false : true"
              />
            <v-text-field
              :label="$t('ActivityForms.activity_subgroup')"
              data-cy="confirmation-sponsor-subgroup-field"
              v-model="subgroup.name"
              dense
              readonly
              v-if="subgroup"
              />
            <v-text-field
              :label="$t('ActivityForms.activity_name')"
              data-cy="confirmation-sponsor-activity-name-field"
              v-model="form.name"
              dense
              readonly
              /></v-col>
        </v-row>
      </validation-observer>
    </template>
  </stepper-form>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</v-card>
</template>

<script>
import { bus } from '@/main'
import _isEmpty from 'lodash/isEmpty'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import StepperForm from '@/components/tools/StepperForm'
import activities from '@/api/activities'
import libConstants from '@/constants/libraries'
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField'

export default {
  components: {
    ConfirmDialog,
    StepperForm,
    SentenceCaseNameField
  },
  props: {
    editedActivity: Object
  },
  computed: {
    title () {
      return (this.editedActivity)
        ? this.$t('ActivityForms.edit_activity')
        : this.$t('ActivityForms.add_activity')
    }
  },
  data () {
    return {
      form: { activity_groupings: [{}] },
      subgroup: {},
      steps: [
        { name: 'request', title: this.$t('ActivityFormsRequested.activity_request') },
        { name: 'sponsor', title: this.$t('ActivityFormsRequested.sponsor_activity') },
        { name: 'confirm', title: this.$t('ActivityFormsRequested.confirmation') }
      ],
      groups: [],
      subGroups: [],
      loading: false,
      helpItems: [],
      activities: [],
      headers: [
        { text: this.$t('ActivityTable.activity_group'), value: 'activity_group.name' },
        { text: this.$t('ActivityTable.activity_subgroup'), value: 'activity_subgroup.name' },
        { text: this.$t('ActivityTable.activity'), value: 'name' }
      ],
      options: {},
      total: 0,
      filteredSubGroups: []
    }
  },
  methods: {
    initForm () {
      if (this.editedActivity) {
        this.activity = this.editedActivity
        this.form = JSON.parse(JSON.stringify(this.activity))
        this.form.activity_groupings = []
        if (!_isEmpty(this.activity)) {
          this.form.activity_groupings.push(this.activity.activity_groupings[0])
          if (this.subGroups.length > 0) {
            this.subgroup = this.subGroups.find(sg => sg.uid === this.activity.activity_groupings[0].activity_subgroup_uid)
          }
        }
      } else {
        this.activity = { activity_groupings: [{}] }
      }
    },
    filterSubGroups () {
      if (!this.form.activity_groupings[0].activity_group_uid) {
        this.filteredSubGroups = []
      }
      this.filteredSubGroups = this.subGroups.filter(el => el.activity_groups.find(o => o.uid === this.form.activity_groupings[0].activity_group_uid) !== undefined)
    },
    getObserver (step) {
      return this.$refs[`observer_${step}`]
    },
    close () {
      this.$emit('close')
      this.form = { activity_groupings: [{}] }
      this.$refs.stepper.reset()
    },
    async submit () {
      this.form.library_name = libConstants.LIBRARY_SPONSOR
      this.form.name_sentence_case = this.form.name.charAt(0).toUpperCase() + this.form.name.slice(1)
      this.form.activity_request_uid = this.editedActivity.uid
      this.$set(this.form, 'activity_subgroup', this.subgroup.uid)
      this.form.activity_groupings[0].activity_subgroup_uid = this.subgroup.uid
      activities.createFromActivityRequest(this.form).then(resp => {
        bus.$emit('warning', { msg: this.$t('ActivityFormsRequested.new_concept_warning') })
        this.close()
        this.$refs.stepper.loading = false
      }, _err => {
        this.$refs.form.working = false
      })
    },
    getGroups () {
      activities.get({ page_size: 0 }, 'activity-groups').then(resp => {
        this.groups = resp.data.items
      })
      activities.get({ page_size: 0 }, 'activity-sub-groups').then(resp => {
        this.subGroups = resp.data.items
        this.filterSubGroups()
        this.subgroup = this.subGroups.find(sg => sg.uid === this.activity.activity_groupings[0].activity_subgroup_uid)
      })
    },
    getActivities () {
      const params = {
        page_number: (this.options.page),
        page_size: this.options.itemsPerPage,
        total_count: true,
        library: 'Sponsor',
        filters: `{"*":{"v":["${this.form.name}"]}}`
      }
      activities.get(params, 'activities').then(resp => {
        const activities = []
        for (const item of resp.data.items) {
          if (item.activity_groupings.length > 0) {
            for (const grouping of item.activity_groupings) {
              activities.push({
                activity_group: { name: grouping.activity_group_name, uid: grouping.activity_group_uid },
                activity_subgroup: { name: grouping.activity_subgroup_name, uid: grouping.activity_subgroup_uid },
                item_key: item.uid + grouping.activity_group_uid + grouping.activity_subgroup_uid,
                ...item
              })
            }
          } else {
            activities.push({
              activity_group: { name: '', uid: '' },
              activity_subgroup: { name: '', uid: '' },
              item_key: item.uid,
              ...item
            })
          }
        }
        this.activities = activities
        this.total = resp.data.total
      })
    }
  },
  mounted () {
    this.getActivities()
    if (this.editedActivity) {
      this.initForm()
    }
    this.getGroups()
  },
  watch: {
    editedActivity: {
      handler (value) {
        if (value) {
          this.initForm()
        }
      },
      immediate: true
    }
  }
}
</script>
