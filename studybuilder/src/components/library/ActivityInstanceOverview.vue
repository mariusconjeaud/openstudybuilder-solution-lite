<template>
<div>
  <v-tabs v-model="tab">
    <v-tab href="#html">{{ $t('_global.overview') }}</v-tab>
    <v-tab href="#yaml">{{ $t('ActivityInstanceOverview.cosmos_yaml') }}</v-tab>
  </v-tabs>
  <v-tabs-items v-model="tab">
    <v-tab-item id="html">
      <v-card elevation="0" class="rounded-0">
        <v-card-text>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.name') }}
            </v-col>
            <v-col cols="6">
              {{ activityInstance.activity_instance.name }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.sentence_case_name') }}
            </v-col>
            <v-col cols="6">
              {{ activityInstance.activity_instance.name_sentence_case }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.definition') }}
            </v-col>
            <v-col cols="6">
              {{ activityInstance.activity_instance.definition }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('ActivityInstanceOverview.class') }}
            </v-col>
            <v-col cols="6">
              {{ activityInstance.activity_instance.activity_instance_class.name }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.abbreviation') }}
            </v-col>
            <v-col cols="2">
              {{ activityInstance.activity_instance.abbreviation }}
            </v-col>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.library') }}
            </v-col>
            <v-col cols="2">
              {{ activityInstance.activity_instance.library_name }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('ActivityInstanceOverview.adam_code') }}
            </v-col>
            <v-col cols="2">
              {{ activityInstance.activity_instance.adam_param_code }}
            </v-col>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('ActivityInstanceOverview.topic_code') }}
            </v-col>
            <v-col cols="2">
              {{ activityInstance.activity_instance.topic_code }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('ActivityInstanceOverview.activity_groupings') }}
            </v-col>
            <v-col cols="6">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr class="text-left">
                      <th scope="col">{{ $t('ActivityInstanceOverview.activity_group') }}</th>
                      <th scope="col">{{ $t('ActivityInstanceOverview.activity_subgroup') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="grouping in activityInstance.activity_groupings" :key="grouping.activity_subgroup_name">
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
            <v-col cols="6">
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
                      <td>{{ activityInstance.activity_groupings[0].activity.name }}</td>
                      <td>{{ activityInstance.activity_groupings[0].activity.definition }}</td>
                      <td>{{ activityInstance.activity_groupings[0].activity.library_name }}</td>
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
            <v-col cols="6">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr class="text-left">
                      <th scope="col">{{ $t('_global.name') }}</th>
                      <th scope="col">{{ $t('ActivityInstanceOverview.ct_term_name') }}</th>
                      <th scope="col">{{ $t('ActivityInstanceOverview.unit_def_name') }}</th>
                      <th scope="col">{{ $t('ActivityInstanceOverview.item_class') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in activityInstance.activity_items" :key="`item-${index}`">
                      <td>{{ item.name }}</td>
                      <td>{{ item.ct_term_name }}</td>
                      <td>{{ item.unit_definition_name }}</td>
                      <td>{{ item.activity_item_class.name }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-tab-item>
    <v-tab-item id="yaml">
      <yaml-viewer :content="yamlVersion" />
    </v-tab-item>
  </v-tabs-items>
</div>
</template>

<script>
import YamlViewer from '@/components/tools/YamlViewer'

export default {
  components: {
    YamlViewer
  },
  props: {
    activityInstance: Object,
    yamlVersion: String
  },
  data () {
    return {
      tab: null
    }
  }
}
</script>
