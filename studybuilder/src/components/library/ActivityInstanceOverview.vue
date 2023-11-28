<template>
<div>
  <base-activity-overview
    :transform-func="transformItem"
    :history-headers="historyHeaders"
    v-on="$listeners"
    v-bind="$attrs"
    >
    <template v-slot:htmlContent="{ itemOverview, item }">
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.name') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity_instance.name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.sentence_case_name') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity_instance.name_sentence_case }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.status') }}
        </v-col>
        <v-col cols="10">
          <status-chip v-if="item" :status="item.status" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.definition') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity_instance.definition }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.class') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity_instance.activity_instance_class.name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.abbreviation') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.abbreviation }}
        </v-col>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.library') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.library_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityForms.nci_concept_id') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity_instance.nci_concept_id }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.adam_code') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.adam_param_code }}
        </v-col>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.topic_code') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.topic_code }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.is_required_for_activity') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.is_required_for_activity | yesno }}
        </v-col>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.is_default_selected_for_activity') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.is_default_selected_for_activity | yesno }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.is_data_sharing') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.is_data_sharing | yesno }}
        </v-col>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.is_legacy_usage') }}
        </v-col>
        <v-col cols="2">
          {{ itemOverview.activity_instance.is_legacy_usage | yesno }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.activity_groupings') }}
        </v-col>
        <v-col cols="10">
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr class="text-left">
                  <th scope="col">{{ $t('ActivityInstanceOverview.activity_group') }}</th>
                  <th scope="col">{{ $t('ActivityInstanceOverview.activity_subgroup') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="grouping in itemOverview.activity_groupings" :key="grouping.activity_subgroup_name">
                  <td>{{ grouping.activity_group.name }}</td>
                  <td>{{ grouping.activity_subgroup.name }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.activity') }}
        </v-col>
        <v-col cols="10">
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr class="text-left">
                  <th scope="col">{{ $t('_global.name') }}</th>
                  <th scope="col">{{ $t('_global.definition') }}</th>
                  <th scope="col">{{ $t('_global.library') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><router-link :to="{ name: 'ActivityOverview', params: { id: itemOverview.activity_groupings[0].activity.uid } }">{{ itemOverview.activity_groupings[0].activity.name }}</router-link></td>
                  <td>{{ itemOverview.activity_groupings[0].activity.definition }}</td>
                  <td>{{ itemOverview.activity_groupings[0].activity.library_name }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityInstanceOverview.items') }}
        </v-col>
        <v-col cols="10">
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr class="text-left">
                  <th scope="col">{{ $t('ActivityInstanceOverview.item_type') }}</th>
                  <th scope="col">{{ $t('_global.name') }}</th>
                  <th scope="col">{{ $t('ActivityInstanceOverview.item_class') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in prepareItems(itemOverview.activity_items)" :key="`item-${index}`">
                  <td>{{ item.type === 'term' ? $t('ActivityInstanceOverview.item_type_term') : $t('ActivityInstanceOverview.item_type_unit') }}</td>
                  <td>
                    <v-simple-table>
                      <tbody>
                        <tr v-for="(name, nameIndex) in item.names" :key="`name-${nameIndex}`">{{ name }}</tr>
                      </tbody>
                    </v-simple-table>
                  </td>
                  <td>{{ item.item_class.name }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>
    </template>
    <template v-slot:itemForm="{ show, item, close }">
      <v-dialog
        :value="show"
        persistent
        max-width="800px"
        content-class="top-dialog"
        >
        <activities-instantiations-form
          @close="close"
          :edited-activity="item"
          />
      </v-dialog>
    </template>
  </base-activity-overview>
</div>
</template>

<script>
import ActivitiesInstantiationsForm from '@/components/library/ActivitiesInstantiationsForm'
import BaseActivityOverview from './BaseActivityOverview'
import StatusChip from '@/components/tools/StatusChip'

export default {
  components: {
    ActivitiesInstantiationsForm,
    BaseActivityOverview,
    StatusChip
  },
  data () {
    return {
      historyHeaders: [
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('ActivityTable.type'), value: 'activity_instance_class.name' },
        { text: this.$t('ActivityTable.activity'), value: 'activities.name', externalFilterSource: 'concepts/activities/activities$name' },
        { text: this.$t('ActivityTable.instance'), value: 'name' },
        { text: this.$t('_global.definition'), value: 'definition' },
        { text: this.$t('ActivityTable.topic_code'), value: 'topic_code' },
        { text: this.$t('ActivityTable.adam_code'), value: 'adam_param_code' },
        { text: this.$t('ActivityTable.is_required_for_activity'), value: 'is_required_for_activity' },
        { text: this.$t('ActivityTable.is_default_selected_for_activity'), value: 'is_default_selected_for_activity' },
        { text: this.$t('ActivityTable.is_data_sharing'), value: 'is_data_sharing' },
        { text: this.$t('ActivityTable.is_legacy_usage'), value: 'is_legacy_usage' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.modified_by'), value: 'user_initials' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ]
    }
  },
  methods: {
    prepareItems (items) {
      const itemsForDisplay = []
      for (const item of items) {
        const newItem = { item_class: item.activity_item_class, names: [] }
        if (item.ct_terms.length > 0) {
          newItem.type = 'term'
          for (const term of item.ct_terms) {
            newItem.names.push(term.name)
          }
        } else if (item.unit_definitions.length > 0) {
          newItem.type = 'unit'
          for (const unit of item.unit_definitions) {
            newItem.names.push(unit.name)
          }
        } else {
          newItem.type = ''
        }
        itemsForDisplay.push(newItem)
      }
      return itemsForDisplay
    },
    transformItem (item) {
      if (item.activity_groupings.length > 0) {
        item.activities = [item.activity_groupings[0].activity]
        item.activity_group = item.activity_groupings[0].activity_group
        item.activity_subgroup = item.activity_groupings[0].activity_subgroup
      } else {
        item.activities = []
      }
      item.item_key = item.uid
    }
  }
}
</script>
