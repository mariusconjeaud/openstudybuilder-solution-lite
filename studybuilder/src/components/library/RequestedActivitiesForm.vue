<template>
<simple-form-dialog
  ref="form"
  :title="title"
  :help-items="helpItems"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <validation-observer ref="observer">
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        data-cy="requestedform-activity-group-class"
        >
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              data-cy="requestedform-activity-group-dropdown"
              :items="groups"
              v-model="form.activity_groupings[0].activity_group_uid"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
              ></v-autocomplete>
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        data-cy="requestedform-activity-subgroup-class"
        >
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_subgroup')"
              data-cy="requestedform-activity-subgroup-dropdown"
              :items="filteredSubGroups"
              v-model="form.activity_groupings[0].activity_subgroup_uid"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
              :disabled="form.activity_groupings[0].activity_group_uid ? false : true"
              ></v-autocomplete>
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        data-cy="requestedform-activity-name-class"
        >
        <v-row>
          <v-col>
            <v-text-field
              :label="$t('ActivityForms.activity_name')"
              data-cy="requestedform-activity-name-field"
              v-model="form.name"
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <sentence-case-name-field
        :name="form.name"
        :initial-name="form.name_sentence_case"
        v-model="form.name_sentence_case"/>
      <validation-provider
        v-slot="{ errors }"
        >
        <v-row>
          <v-col>
            <v-text-field
              :label="$t('ActivityFormsRequested.abbreviation')"
              data-cy="requestedform-abbreviation-field"
              v-model="form.abbreviation"
              :error-messages="errors"
              dense
              clearable
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        >
        <v-row>
          <v-col>
            <v-textarea
              :label="$t('ActivityFormsRequested.definition')"
              data-cy="requestedform-definition-field"
              v-model="form.definition"
              :error-messages="errors"
              dense
              clearable
              auto-grow
              rows="1"
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        data-cy="requestedform-rationale-for-request-class"
        >
        <v-row>
          <v-col>
            <v-textarea
              :label="$t('ActivityFormsRequested.rationale_for_request')"
              data-cy="requestedform-rationale-for-request-field"
              v-model="form.request_rationale"
              :error-messages="errors"
              dense
              clearable
              auto-grow
              rows="1"
              />
          </v-col>
        </v-row>
      </validation-provider>
      <validation-provider
        v-if="isEdit"
        v-slot="{ errors }"
        >
        <v-row>
          <v-col>
            <label class="v-label">{{ $t('ActivityForms.reason_for_change') }}</label>
            <v-textarea
              v-model="form.change_description"
              data-cy="requestedform-change-description-field"
              :error-messages="errors"
              dense
              clearable
              auto-grow
              rows="1"
              />
          </v-col>
        </v-row>
      </validation-provider>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import { bus } from '@/main'
import _isEqual from 'lodash/isEqual'
import _isEmpty from 'lodash/isEmpty'
import activities from '@/api/activities'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import libConstants from '@/constants/libraries'
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField'

export default {
  components: {
    SimpleFormDialog,
    SentenceCaseNameField
  },
  props: {
    editedActivity: Object,
    open: Boolean
  },
  computed: {
    isEdit () {
      return !_isEmpty(this.editedActivity)
    },
    title () {
      return (!_isEmpty(this.editedActivity))
        ? this.$t('ActivityForms.edit_activity_request')
        : this.$t('ActivityForms.add_activity_request')
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
      form: {
        activity_groupings: [{}]
      },
      groups: [],
      subGroups: [],
      libraries: [],
      helpItems: []
    }
  },
  methods: {
    initForm (value) {
      this.form = JSON.parse(JSON.stringify(value))
      this.form.activity_groupings = [{}]
      if (!_isEmpty(value)) {
        const grouping = [{}]
        if (value.activity_group) {
          grouping[0].activity_group_name = value.activity_group.name
          grouping[0].activity_group_uid = value.activity_group.uid
        }
        if (value.activity_subgroup) {
          grouping[0].activity_subgroup_name = value.activity_subgroup.name
          grouping[0].activity_subgroup_uid = value.activity_subgroup.uid
        }
        this.$set(this.form, 'activity_groupings', grouping)
      }
      this.$store.commit('form/SET_FORM', this.form)
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
    close () {
      this.$emit('close')
      this.form = { activity_groupings: [{}] }
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.observer.reset()
    },
    async submit () {
      this.form.library_name = libConstants.LIBRARY_REQUESTED
      this.form.name_sentence_case = this.form.name.charAt(0).toUpperCase() + this.form.name.slice(1)
      if (!this.isEdit) {
        activities.create(this.form, 'activities').then(resp => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_created') })
          this.close()
        }, _err => {
          this.$refs.form.working = false
        })
      } else {
        activities.update(this.editedActivity.uid, this.form, 'activities').then(resp => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_updated') })
          this.close()
        }, _err => {
          this.$refs.form.working = false
        })
      }
    },
    getGroupsAndSubGroups () {
      activities.get({ page_size: 0 }, 'activity-sub-groups').then(resp => {
        this.subGroups = resp.data.items
      })
      activities.get({ page_size: 0 }, 'activity-groups').then(resp => {
        this.groups = resp.data.items
      })
    }
  },
  mounted () {
    if (this.isEdit) {
      this.initForm(this.editedActivity)
    }
    this.getGroupsAndSubGroups()
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
