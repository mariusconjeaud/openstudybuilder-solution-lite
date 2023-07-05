<template>
<div>
  <v-tabs v-model="tab">
    <v-tab href="#html">{{ $t('_global.overview') }}</v-tab>
    <v-tab href="#yaml">{{ $t('ActivityOverview.cosmos_yaml') }}</v-tab>
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
              {{ activity.activity.name }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.sentence_case_name') }}
            </v-col>
            <v-col cols="6">
              {{ activity.activity.name_sentence_name }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.definition') }}
            </v-col>
            <v-col cols="6">
              {{ activity.activity.definition }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.abbreviation') }}
            </v-col>
            <v-col cols="2">
              {{ activity.activity.abbreviation }}
            </v-col>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('_global.library') }}
            </v-col>
            <v-col cols="2">
              {{ activity.activity.library_name }}
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('ActivityOverview.activity_groups') }}
            </v-col>
            <v-col cols="6">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr class="text-left">
                      <th scope="col">{{ $t('_global.name') }}</th>
                      <th scope="col">{{ $t('_global.definition') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="group in activity.activity_groups" :key="group.name">
                      <td>{{ group.name }}</td>
                      <td>{{ group.definition }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2" class="font-weight-bold">
              {{ $t('ActivityOverview.activity_subgroups') }}
            </v-col>
            <v-col cols="6">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr class="text-left">
                      <th scope="col">{{ $t('_global.name') }}</th>
                      <th scope="col">{{ $t('_global.definition') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="subgroup in activity.activity_subgroups" :key="subgroup.name">
                      <td>{{ subgroup.name }}</td>
                      <td>{{ subgroup.definition }}</td>
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
            <v-col cols="6">
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
                    <tr v-for="(item, index) in activity.activity_instances" :key="`item-${index}`">
                      <td>{{ item.name }}</td>
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
    activity: Object,
    yamlVersion: String
  },
  data () {
    return {
      tab: null
    }
  }
}
</script>
