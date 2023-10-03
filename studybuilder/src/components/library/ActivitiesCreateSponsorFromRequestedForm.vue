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
              :items="filteredSubGroups"
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
              :label="$t('ActivityForms.name')"
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
          <v-col cols="5">
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-autocomplete
                :label="$t('ActivityForms.activity_group')"
                :items="groups"
                v-model="form.activity_groupings[0].activity_group_uid"
                item-text="name"
                item-value="uid"
                dense
                clearable
                return-object
                :error-messages="errors"
                />
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-autocomplete
                :label="$t('ActivityForms.activity_subgroup')"
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
                :label="$t('ActivityForms.name')"
                v-model="form.name"
                dense
                clearable
                @input="getActivities"
                :error-messages="errors"
                />
            </validation-provider>
            <v-text-field
              :label="$t('ActivityFormsRequested.abbreviation')"
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
                v-model="form.request_rationale"
                dense
                clearable
                auto-grow
                rows="1"
                :error-messages="errors"
                />
              </validation-provider>
          </v-col>
          <v-col cols="7">
            <v-data-table
              :headers="headers"
              :items="activities"
              :options.sync="options"
              :server-items-length="total"
              @pagination="getActivities"
              :items-per-page="5"
              item-key="item-key">
            </v-data-table>
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
              v-model="activity.activity_groupings[0].activity_group_name"
              dense
              readonly
              v-if="activity.activity_group"
              />
            <v-text-field
              :label="$t('ActivityForms.activity_subgroup')"
              v-model="activity.activity_groupings[0].activity_subgroup_name"
              dense
              readonly
              v-if="activity.activity_groupings[0].activity_group_uid ? false : true"
              />
            <v-text-field
              :label="$t('ActivityForms.name')"
              v-model="activity.name"
              dense
              readonly
              />
          </v-col>
          <v-col cols="6">
            <div class="text-h5 mb-8">{{ $t('ActivityFormsRequested.new_sponsor_concept')  }}</div>
            <v-text-field
              :label="$t('ActivityForms.activity_group')"
              v-model="form.activity_groupings[0].activity_group_name"
              dense
              readonly
              v-if="activity.activity_groupings[0].activity_group_uid ? false : true"
              />
            <v-text-field
              :label="$t('ActivityForms.activity_subgroup')"
              v-model="subgroup.name"
              dense
              readonly
              v-if="subgroup"
              />
            <v-text-field
              :label="$t('ActivityForms.name')"
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
        ? this.$t('ActivityForms.edit_group')
        : this.$t('ActivityForms.add_group')
    },
    filteredSubGroups () {
      if (!this.form.activity_groupings[0].activity_group_uid) {
        return []
      }
      return this.subGroups.filter(el => el.activity_groups.find(o => o.uid === this.form.activity_groupings[0].activity_group_uid) !== undefined)
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
      total: 0
    }
  },
  methods: {
    initForm () {
      if (this.editedActivity) {
        this.activity = this.editedActivity
        this.form = JSON.parse(JSON.stringify(this.activity))
        this.form.activity_groupings = [{}]
        if (!_isEmpty(this.activity)) {
          const grouping = [{}]
          if (this.activity.activity_group) {
            grouping[0].activity_group_name = this.activity.activity_group.name
            grouping[0].activity_group_uid = this.activity.activity_group.uid
          }
          if (this.activity.activity_subgroup) {
            grouping[0].activity_subgroup_name = this.activity.activity_subgroup.name
            grouping[0].activity_subgroup_uid = this.activity.activity_subgroup.uid
          }
          this.$set(this.form, 'activity_groupings', grouping)
        }
      } else {
        this.activity = { activity_groupings: [{}] }
      }

      this.subgroup = this.form.activity_subgroup
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
      activities.createFromActivityRequest(this.form).then(resp => {
        bus.$emit('warning', { msg: this.$t('ActivityFormsRequested.new_concept_warning') })
        this.close()
      })
      this.$refs.stepper.loading = false
    },
    getGroups () {
      activities.get({ page_size: 0 }, 'activity-groups').then(resp => {
        this.groups = resp.data.items
      })
      activities.get({ page_size: 0 }, 'activity-sub-groups').then(resp => {
        this.subGroups = resp.data.items
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
