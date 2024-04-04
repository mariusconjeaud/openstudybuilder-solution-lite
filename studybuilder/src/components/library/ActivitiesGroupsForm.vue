<template>
<div>
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
          v-if="subgroup"
          data-cy="groupform-subgroup-class"
          >
          <v-row>
            <v-col>
              <v-autocomplete
                v-model="form.activity_groups"
                :items="groups"
                :label="$t('ActivityForms.groups')"
                data-cy="groupform-activity-group-dropdown"
                item-text="name"
                item-value="uid"
                dense
                clearable
                multiple
                :error-messages="errors"
                />
            </v-col>
          </v-row>
        </validation-provider>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          data-cy="groupform-activity-group-class"
          >
          <v-row>
            <v-col>
              <v-text-field
                v-model="form.name"
                :label="subgroup ? $t('ActivityForms.subgroup_name') : $t('ActivityForms.group_name')"
                data-cy="groupform-activity-group-field"
                :error-messages="errors"
                />
            </v-col>
          </v-row>
        </validation-provider>
        <sentence-case-name-field
          :name="form.name"
          :initial-name="form.name_sentence_case"
          v-model="form.name_sentence_case"/>
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.abbreviation"
              :label="$t('ActivityForms.abbreviation')"
              data-cy="groupform-abbreviation-field"
              />
          </v-col>
        </v-row>
        <validation-provider
          v-slot="{ errors }"
          rules="required"
          data-cy="groupform-definition-class"
          >
          <v-row>
            <v-col>
              <v-textarea
                v-model="form.definition"
                :label="$t('ActivityForms.definition')"
                data-cy="groupform-definition-field"
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
          v-if="editing"
          >
          <v-row>
            <v-col>
              <v-textarea
                v-model="form.change_description"
                :label="$t('ActivityForms.change_description')"
                data-cy="groupform-change-description-field"
                :error-messages="errors"
                auto-grow
                rows="1"
                />
            </v-col>
        </v-row>
        </validation-provider>
      </validation-observer>
    </template>
  </simple-form-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import { bus } from '@/main'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import _isEqual from 'lodash/isEqual'
import _isEmpty from 'lodash/isEmpty'
import activities from '@/api/activities'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField'

export default {
  components: {
    ConfirmDialog,
    SimpleFormDialog,
    SentenceCaseNameField
  },
  props: {
    open: Boolean,
    editedGroupOrSubgroup: Object,
    subgroup: Boolean
  },
  computed: {
    title () {
      if (!this.subgroup) {
        return !_isEmpty(this.editedGroupOrSubgroup)
          ? this.$t('ActivityForms.edit_group')
          : this.$t('ActivityForms.add_group')
      } else {
        return !_isEmpty(this.editedGroupOrSubgroup)
          ? this.$t('ActivityForms.edit_subgroup')
          : this.$t('ActivityForms.add_subgroup')
      }
    }
  },
  data () {
    return {
      form: {},
      steps: [
        { name: 'select', title: this.$t('ActivityForms.select_type') },
        { name: 'details', title: this.$t('ActivityForms.add_additional_data') }
      ],
      groups: [],
      loading: false,
      editing: false,
      libraries: [],
      helpItems: [
        'ActivityFormsGrouping.name',
        'ActivityFormsGrouping.definition'
      ]
    }
  },
  methods: {
    initForm (value) {
      this.editing = true
      this.form = {
        name: value.name,
        name_sentence_case: value.name_sentence_case,
        definition: value.definition,
        change_description: '',
        abbreviation: value.abbreviation
      }
      if (!_isEmpty(value)) {
        if (value.activity_groups) {
          const uids = []
          for (const item of value.activity_groups) {
            uids.push(item.uid)
          }
          this.$set(this.form, 'activity_groups', uids)
        }
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
        if (await this.$refs.confirm.open(this.$t('_global.cancel_changes'), options)) {
          this.close()
        }
      }
    },
    close () {
      this.$emit('close')
      this.form = {}
      this.editing = false
      this.$refs.form.working = false
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.observer.reset()
    },
    async submit () {
      this.form.library_name = 'Sponsor' // Hardcoded for now at the Sinna and Mikkel request
      if (!this.editedGroupOrSubgroup) {
        if (!this.subgroup) {
          activities.create(this.form, 'activity-groups').then(resp => {
            bus.$emit('notification', { msg: this.$t('ActivityForms.group_created') })
            this.close()
          }, _err => {
            this.$refs.form.working = false
          })
        } else {
          activities.create(this.form, 'activity-sub-groups').then(resp => {
            bus.$emit('notification', { msg: this.$t('ActivityForms.subgroup_created') })
            this.close()
          }, _err => {
            this.$refs.form.working = false
          })
        }
      } else {
        if (!this.subgroup) {
          activities.update(this.editedGroupOrSubgroup.uid, this.form, 'activity-groups').then(resp => {
            bus.$emit('notification', { msg: this.$t('ActivityForms.group_updated') })
            this.close()
          }, _err => {
            this.$refs.form.working = false
          })
        } else {
          activities.update(this.editedGroupOrSubgroup.uid, this.form, 'activity-sub-groups').then(resp => {
            bus.$emit('notification', { msg: this.$t('ActivityForms.subgroup_updated') })
            this.close()
          }, _err => {
            this.$refs.form.working = false
          })
        }
      }
    },
    checkIfEqual () {
      if (_isEqual(this.form.change_description, this.editedGroupOrSubgroup.change_description) &&
          _isEqual(this.form.definition, this.editedGroupOrSubgroup.definition) &&
          _isEqual(this.form.name, this.editedGroupOrSubgroup.name)) {
        return true
      } else {
        return false
      }
    },
    getGroups () {
      activities.get({ page_size: 0, filters: { status: { v: ['Final'] } } }, 'activity-groups').then(resp => {
        this.groups = resp.data.items
      })
    }
  },
  mounted () {
    if (!_isEmpty(this.editedGroupOrSubgroup)) {
      this.initForm(this.editedGroupOrSubgroup)
    }
    this.getGroups()
  },
  watch: {
    editedGroupOrSubgroup: {
      handler (value) {
        if (!_isEmpty(value)) {
          this.initForm(value)
        }
      },
      immediate: true
    }
  }
}
</script>
