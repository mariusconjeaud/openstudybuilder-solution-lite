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
        >
        <v-row>
          <v-col>
            <v-autocomplete
              :label="$t('ActivityForms.activity_group')"
              :items="groups"
              v-model="form.activity_group"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
              return-object
              ></v-autocomplete>
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
              v-model="form.activity_subgroup"
              item-text="name"
              item-value="uid"
              :error-messages="errors"
              dense
              clearable
              :disabled="form.activity_group ? false : true"
              ></v-autocomplete>
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
              :label="$t('ActivityForms.name')"
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
              :label="$t('ActivityFormsRequested.abbreviation')"
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
        >
        <v-row>
          <v-col>
            <v-textarea
              :label="$t('ActivityFormsRequested.rationale_for_request')"
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

export default {
  components: {
    SimpleFormDialog
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
        ? this.$t('ActivityForms.edit_activity')
        : this.$t('ActivityForms.add_activity')
    },
    filteredSubGroups () {
      if (!this.form.activity_group) {
        return []
      }
      return this.subGroups.filter(el => el.activity_group.uid === this.form.activity_group.uid)
    }
  },
  data () {
    return {
      form: {},
      groups: [],
      subGroups: [],
      libraries: [],
      helpItems: []
    }
  },
  methods: {
    initForm (value) {
      this.form = JSON.parse(JSON.stringify(value))
      if (this.form.activity_subgroup) {
        this.$set(this.form, 'activity_subgroup', this.form.activity_subgroup.uid)
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
      this.form = {}
      this.$store.commit('form/CLEAR_FORM')
      this.$refs.observer.reset()
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      this.form.library_name = libConstants.LIBRARY_REQUESTED
      this.form.name_sentence_case = this.form.name.charAt(0).toUpperCase() + this.form.name.slice(1)
      if (!this.isEdit) {
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
