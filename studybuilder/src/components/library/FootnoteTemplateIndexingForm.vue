<template>
<template-indexing-form
  :form="form"
  :template="template"
  >
  <template v-slot:templateIndexFields>
    <not-applicable-field
      :checked="template && (!template.activity_groups || !template.activity_groups.length)"
      :clean-function="value => $set(form, 'activity_group', null)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <v-row>
            <v-col cols="11">
              <v-autocomplete
                v-model="form.activity_group"
                :label="$t('FootnoteTemplateForm.group')"
                data-cy="template-activity-group"
                :items="groups"
                item-text="name"
                item-value="uid"
                :error-messages="errors"
                dense
                clearable
                @change="setSubGroups"
                :disabled="notApplicable"
                />
            </v-col>
          </v-row>
        </validation-provider>
      </template>
    </not-applicable-field>
    <not-applicable-field
      :checked="template && (!template.activity_subgroups || !template.activity_subgroups.length)"
      :clean-function="value => $set(form, 'activity_subgroups', null)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <v-row>
            <v-col cols="11">
              <v-autocomplete
                v-model="form.activity_subgroups"
                :label="$t('FootnoteTemplateForm.sub_group')"
                data-cy="template-activity-sub-group"
                :items="subGroups"
                item-text="name"
                item-value="uid"
                :error-messages="errors"
                dense
                clearable
                multiple
                @change="setActivities"
                :disabled="notApplicable"
                />
            </v-col>
          </v-row>
        </validation-provider>
      </template>
    </not-applicable-field>
    <not-applicable-field
      :checked="template && (!template.activities || !template.activities.length)"
      :clean-function="value => $set(form, 'activities', null)"
      >
      <template v-slot:mainField="{ notApplicable }">
        <validation-provider
          v-slot="{ errors }"
          name="activity"
          :rules="`requiredIfNotNA:${notApplicable}`"
          >
          <v-row>
            <v-col cols="11">
              <v-autocomplete
                v-model="form.activities"
                :label="$t('FootnoteTemplateForm.activity')"
                data-cy="template-activity-activity"
                :items="activities"
                item-text="name"
                return-object
                :error-messages="errors"
                dense
                clearable
                multiple
                :disabled="notApplicable"
                />
            </v-col>
          </v-row>
        </validation-provider>
      </template>
    </not-applicable-field>
  </template>
</template-indexing-form>
</template>

<script>
import activities from '@/api/activities'
import NotApplicableField from '@/components/tools/NotApplicableField'
import TemplateIndexingForm from './TemplateIndexingForm'

export default {
  components: {
    NotApplicableField,
    TemplateIndexingForm
  },
  props: {
    form: Object,
    template: Object
  },
  data () {
    return {
      activities: [],
      groups: [],
      subGroups: []
    }
  },
  methods: {
    preparePayload (form) {
      const result = {}
      if (form.activity_group) {
        result.activity_group_uids = [form.activity_group]
      } else {
        result.activity_group_uids = []
      }
      if (form.activity_group && form.activity_group.length) {
        result.activity_subgroup_uids = []
        for (const item of form.activity_subgroups) {
          const itemUid = (typeof item !== 'string') ? item.uid : item
          result.activity_subgroup_uids.push(itemUid)
        }
      } else {
        form.activity_subgroup_uids = []
      }
      if (form.activities) {
        result.activity_uids = form.activities.map(item => item.uid)
      } else {
        result.activity_uids = []
      }
      return result
    },
    async setSubGroups (group, noSubgroupReset) {
      if (group) {
        const resp = await activities.getSubGroups(group)
        this.subGroups = resp.data.items
      }
      if (!noSubgroupReset) {
        this.$set(this.form, 'activity_subgroups', [])
        this.$set(this.form, 'activities', [])
      }
    },
    setActivities (subgroupUids) {
      this.activities = []
      for (const sg of subgroupUids) {
        activities.getSubGroupActivities(sg).then(resp => {
          this.activities = this.activities.concat(resp.data.items)
        })
      }
    }
  },
  created () {
    if (!this.groups.length) {
      activities.getGroups({ page_size: 0 }).then(resp => {
        this.groups = resp.data.items
      })
    }
  },
  watch: {
    template: {
      handler: async function (value) {
        if (value && value.activity_groups && value.activity_groups.length) {
          if (!this.groups.length) {
            const resp = await activities.getGroups()
            this.groups = resp.data.items
          }
          const activityGroupUid = (typeof this.template.activity_groups[0] !== 'string')
            ? this.template.activity_groups[0].uid
            : this.template.activity_groups[0]
          this.$set(this.form, 'activity_group', activityGroupUid)
          await this.setSubGroups(this.form.activity_group, true)
          if (!this.form.activity_subgroups) {
            this.$set(this.form, 'activity_subgroups', value.activity_subgroups)
          }
          const subgroupUids = this.form.activity_subgroups.map(g => g.uid)
          await this.setActivities(subgroupUids, true)
          if (!this.form.activities) {
            this.$set(this.form, 'activities', value.activities)
          }
        }
      },
      immediate: true
    }
  }
}
</script>
