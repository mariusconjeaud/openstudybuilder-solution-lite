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
      <v-row>
        <v-col>
          <v-text-field
            :label="$t('_global.library')"
            v-model="form.library_name"
            dense
            disabled
            />
        </v-col>
      </v-row>
      <validation-provider
        v-slot="{ errors }"
        rules="required"
        >
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              :items="groups"
              v-model="form.activity_groupings[0].activity_group_uid"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
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
            <v-text-field
              :label="$t('ActivityForms.activity_name')"
              v-model="form.name"
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
            <v-text-field
              :label="$t('ActivityForms.abbreviation')"
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
        rules="required"
        >
        <v-row>
          <v-col>
            <v-textarea
              :label="$t('ActivityForms.definition')"
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
        v-if="editing"
        v-slot="{ errors }"
        >
        <v-row>
          <v-col>
            <label class="v-label">{{ $t('ActivityForms.reason_for_change') }}</label>
            <v-textarea
              v-model="form.change_description"
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
import constants from '@/constants/libraries.js'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    editedActivity: Object,
    open: Boolean
  },
  computed: {
    title () {
      return (!_isEmpty(this.editedActivity))
        ? this.$t('ActivityForms.edit_activity')
        : this.$t('ActivityForms.add_activity')
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
        library_name: constants.LIBRARY_SPONSOR,
        activity_groupings: [{}]
      },
      groups: [],
      subGroups: [],
      libraries: [],
      helpItems: [
        'ActivityForms.activity_subgroup',
        'ActivityForms.name',
        'ActivityForms.definition'
      ],
      editing: false
    }
  },
  methods: {
    initForm (value) {
      this.editing = true
      this.form = {
        name: value.name,
        name_sentence_case: '',
        definition: value.definition,
        abbreviation: value.abbreviation,
        change_description: '',
        library_name: value.library_name,
        activity_groupings: [{}]
      }
      if (!_isEmpty(value)) {
        this.$set(this.form, 'name_sentence_case', value.name.charAt(0).toUpperCase() + value.name.slice(1))
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
      this.form = {
        library_name: constants.LIBRARY_SPONSOR
      }
      this.editing = false
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.observer.reset()
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      this.form.name_sentence_case = this.form.name.charAt(0).toUpperCase() + this.form.name.slice(1)
      if (!this.editedActivity) {
        activities.create(this.form, 'activities').then(resp => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_created') })
          this.close()
        })
      } else {
        activities.update(this.editedActivity.uid, this.form, 'activities').then(resp => {
          bus.$emit('notification', { msg: this.$t('ActivityForms.activity_updated') })
          this.close()
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
    if (!_isEmpty(this.editedActivity)) {
      this.initForm(this.editedActivity)
    }
    this.getGroupsAndSubGroups()
  },
  watch: {
    editedActivity: {
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
