<template>
<template-indexing-form
  :form="form"
  :template="template"
  >
  <template v-slot:templateIndexFields>
    <validation-provider
      v-slot="{ errors }"
      rules="required"
      >
      <v-row>
        <v-col cols="11">
          <v-autocomplete
            v-model="form.activity_group"
            :label="$t('ActivityDescriptionTemplateForm.group')"
            :items="groups"
            item-text="name"
            item-value="uid"
            :error-messages="errors"
            dense
            clearable
            @change="setSubGroups"
            />
        </v-col>
      </v-row>
    </validation-provider>
    <validation-provider
      v-slot="{ errors }"
      rules="required"
      >
      <v-row>
        <v-col cols="11">
          <v-autocomplete
            v-model="form.activity_subgroups"
            :label="$t('ActivityDescriptionTemplateForm.sub_group')"
            :items="subGroups"
            item-text="name"
            item-value="uid"
            :error-messages="errors"
            dense
            clearable
            multiple
            @change="setActivities"
            />
        </v-col>
      </v-row>
    </validation-provider>
    <not-applicable-field
      :checked="template && !template.activities"
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
                :label="$t('ActivityDescriptionTemplateForm.activity')"
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
      result.activity_group_uids = [form.activity_group]
      result.activity_subgroup_uids = []
      for (const item of form.activity_subgroups) {
        const itemUid = (typeof item !== 'string') ? item.uid : item
        result.activity_subgroup_uids.push(itemUid)
      }
      if (form.activities) {
        result.activity_uids = form.activities.map(item => item.uid)
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
    activities.getGroups().then(resp => {
      this.groups = resp.data.items
    })
  },
  watch: {
    template: {
      handler: async function (value) {
        if (value && value.activity_groups && value.activity_groups.length) {
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
