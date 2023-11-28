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
      <v-card style="position: relative" class="sub-v-card">
        <v-card-title style="position: relative">
          {{ $t('ActivityForms.activity_groupings') }}
        </v-card-title>
        <v-btn
          color="primary"
          absolute
          top
          right
          fab
          x-small
          @click="addGrouping"
          >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-card-text>
          <v-card v-for="(grouping, index) in form.activity_groupings" :key="index" class="sub-v-card">
            <v-card-text style="position: relative">
              <validation-provider
                v-slot="{ errors }"
                rules="required"
                >
                <v-autocomplete
                  :label="$t('ActivityForms.activity_group')"
                  :items="groups"
                  v-model="form.activity_groupings[index].activity_group_uid"
                  item-text="name"
                  item-value="uid"
                  :error-messages="errors"
                  dense
                  clearable
                  />
              </validation-provider>
              <validation-provider
                v-slot="{ errors }"
                rules="required"
                >
                <v-autocomplete
                  :label="$t('ActivityForms.activity_subgroup')"
                  :items="filteredSubGroups(index)"
                  v-model="form.activity_groupings[index].activity_subgroup_uid"
                  item-text="name"
                  item-value="uid"
                  :error-messages="errors"
                  dense
                  clearable
                  :disabled="form.activity_groupings[index].activity_group_uid ? false : true"
                  />
              </validation-provider>
            </v-card-text>
            <v-btn
              v-if="index > 0"
              color="error"
              absolute
              top
              right
              fab
              x-small
              @click="removeGrouping(index)"
              >
              <v-icon>mdi-delete-outline</v-icon>
            </v-btn>
          </v-card>
        </v-card-text>
      </v-card>
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
      <sentence-case-name-field
        :name="form.name"
        :initial-name="form.name_sentence_case"
        v-model="form.name_sentence_case"/>
      <v-row>
        <v-col>
          <v-text-field
            :label="$t('ActivityForms.nci_concept_id')"
            v-model="form.nci_concept_id"
            :error-messages="errors"
            dense
            clearable
            />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-checkbox
            :label="$t('ActivityForms.is_data_collected')"
            v-model="form.is_data_collected">
          </v-checkbox>
        </v-col>
      </v-row>
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
import SentenceCaseNameField from '@/components/tools/SentenceCaseNameField'
import constants from '@/constants/libraries.js'

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
    title () {
      return (!_isEmpty(this.editedActivity))
        ? this.$t('ActivityForms.edit_activity')
        : this.$t('ActivityForms.add_activity')
    }
  },
  data () {
    return {
      form: {
        library_name: constants.LIBRARY_SPONSOR,
        activity_groupings: [{}],
        is_data_collected: true
      },
      errors: [],
      groups: [],
      subGroups: [],
      libraries: [],
      helpItems: [
        'ActivityForms.activity_group',
        'ActivityForms.activity_subgroup',
        'ActivityForms.name',
        'ActivityForms.nci_concept_id',
        'ActivityForms.is_data_collected',
        'ActivityForms.abbreviation',
        'ActivityForms.definition',
        'ActivityForms.activity_name'
      ],
      editing: false
    }
  },
  methods: {
    filteredSubGroups (index) {
      if (!this.form.activity_groupings[index].activity_group_uid) {
        return []
      }
      return this.subGroups.filter(el => el.activity_groups.find(o => o.uid === this.form.activity_groupings[index].activity_group_uid) !== undefined)
    },
    initForm (value) {
      this.editing = true
      this.form = {
        name: value.name,
        name_sentence_case: value.name_sentence_case,
        nci_concept_id: value.nci_concept_id,
        is_data_collected: value.is_data_collected,
        definition: value.definition,
        abbreviation: value.abbreviation,
        change_description: '',
        library_name: value.library_name,
        activity_groupings: [{}]
      }
      if (!_isEmpty(value)) {
        this.$set(this.form, 'activity_groupings', value.activity_groupings)
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
        library_name: constants.LIBRARY_SPONSOR,
        activity_groupings: [{}],
        is_data_collected: true
      }
      this.editing = false
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.observer.reset()
    },
    async submit () {
      if (!this.editedActivity) {
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
    },
    addGrouping () {
      this.form.activity_groupings.push({})
    },
    removeGrouping (index) {
      this.form.activity_groupings.splice(index, 1)
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
<style>
.sub-v-card {
  margin-bottom: 25px;
}
</style>
