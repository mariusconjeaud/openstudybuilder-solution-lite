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
          {{ itemOverview.activity.name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.sentence_case_name') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity.name_sentence_case }}
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
          {{ itemOverview.activity.definition }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.abbreviation') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity.abbreviation }}
        </v-col>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('_global.library') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity.library_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityForms.nci_concept_id') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity.nci_concept_id }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityOverview.is_data_collected') }}
        </v-col>
        <v-col cols="10">
          {{ itemOverview.activity.is_data_collected | yesno }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('ActivityOverview.activity_groupings') }}
        </v-col>
        <v-col cols="10">
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr class="text-left">
                  <th scope="col">{{ $t('ActivityOverview.activity_group') }}</th>
                  <th scope="col">{{ $t('ActivityOverview.activity_subgroup') }}</th>
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
          {{ $t('ActivityOverview.instances') }}
        </v-col>
        <v-col cols="10">
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr class="text-left">
                  <th scope="col">{{ $t('_global.name') }}</th>
                  <th scope="col">{{ $t('_global.definition') }}</th>
                  <th scope="col">{{ $t('ActivityOverview.class') }}</th>
                  <th scope="col">{{ $t('ActivityOverview.topic_code') }}</th>
                  <th scope="col">{{ $t('ActivityOverview.adam_code') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in itemOverview.activity_instances" :key="`item-${index}`">
                  <td><router-link :to="{ name: 'ActivityInstanceOverview', params: { id: item.uid } }">{{ item.name }}</router-link></td>
                  <td>{{ item.definition }}</td>
                  <td>{{ item.activity_instance_class.name }}</td>
                  <td>{{ item.topic_code }}</td>
                  <td>{{ item.adam_param_code }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>
    </template>
    <template v-slot:itemForm="{ show, item, close }">
      <activities-form
        :open="show"
        @close="close"
        :edited-activity="item"
        />
    </template>
  </base-activity-overview>
</div>
</template>

<script>
import ActivitiesForm from '@/components/library/ActivitiesForm'
import BaseActivityOverview from './BaseActivityOverview'
import StatusChip from '@/components/tools/StatusChip'

export default {
  components: {
    ActivitiesForm,
    BaseActivityOverview,
    StatusChip
  },
  data () {
    return {
      historyHeaders: [
        { text: this.$t('_global.library'), value: 'library_name' },
        { text: this.$t('ActivityTable.activity_group'), value: 'activity_group.name', externalFilterSource: 'concepts/activities/activity-groups$name', width: '15%', exludeFromHeader: ['is_data_collected'] },
        { text: this.$t('ActivityTable.activity_subgroup'), value: 'activity_subgroup.name', externalFilterSource: 'concepts/activities/activity-sub-groups$name', width: '15%', exludeFromHeader: ['is_data_collected'] },
        { text: this.$t('ActivityTable.activity_name'), value: 'name', externalFilterSource: 'concepts/activities/activities$name' },
        { text: this.$t('ActivityTable.sentence_case_name'), value: 'name_sentence_case' },
        { text: this.$t('ActivityTable.abbreviation'), value: 'abbreviation' },
        { text: this.$t('ActivityTable.is_data_collected'), value: 'is_data_collected' },
        { text: this.$t('_global.modified'), value: 'start_date' },
        { text: this.$t('_global.status'), value: 'status' },
        { text: this.$t('_global.version'), value: 'version' }
      ]
    }
  },
  methods: {
    transformItem (item) {
      if (item.activity_groupings.length > 0) {
        const groups = []
        const subgroups = []
        for (const grouping of item.activity_groupings) {
          groups.push(grouping.activity_group_name)
          subgroups.push(grouping.activity_subgroup_name)
        }
        item.activity_group = { name: groups }
        item.activity_subgroup = { name: subgroups }
        item.item_key = item.uid
      } else {
        item.activity_group = { name: '' }
        item.activity_subgroup = { name: '' }
        item.item_key = item.uid
      }
    }
  }
}
</script>
