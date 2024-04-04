<template>
<div>
  <div class="d-flex page-title">
    {{ `${$t('StudyActivity.study_activity')}: ${activity.activity.name}` }}
    <v-spacer />
    <v-btn
      fab
      small
      @click="close"
      :title="$t('_global.close')"
      class="ml-2"
      >
      <v-icon>{{ 'mdi-close' }}</v-icon>
    </v-btn>
  </div>
  <v-card elevation="0" class="rounded-0">
    <v-card-text>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyActivity.flowchart_group') }}
        </v-col>
        <v-col cols="2">
          {{ activity.study_soa_group.soa_group_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyActivity.activity') }}
        </v-col>
        <v-col cols="2">
          <router-link :to="{ name: 'ActivityOverview', params: { id: activity.activity.uid } }">
            {{ activity.activity.name }}
          </router-link>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyActivity.activity_group') }}
        </v-col>
        <v-col cols="2">
          {{ activity.study_activity_group.activity_group_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyActivity.activity_sub_group') }}
        </v-col>
        <v-col cols="2">
          {{ activity.study_activity_subgroup.activity_subgroup_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyActivity.data_collection') }}
        </v-col>
        <v-col cols="2">
          {{ activity.activity.is_data_collected|yesno }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyActivity.other_groupings') }}
        </v-col>
        <v-col cols="10">
          <v-data-table
            class="elevation-0"
            :headers="groupingsHeaders"
            :items="activity.activity.activity_groupings"
            item-key="activity_subgroup_uid"
            light
            hide-default-footer
            >
            <template v-slot:item.activity_name="{ item }">
              <router-link :to="{ name: 'ActivityOverview', params: { id: activity.activity.uid } }">
                {{ item.activity_name }}
              </router-link>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import study from '@/api/study'

export default {
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  mounted () {
    study.getStudyActivity(this.$route.params.study_id, this.$route.params.id).then(resp => {
      this.activity = resp.data
    })
  },
  data () {
    return {
      activity: {},
      groupingsHeaders: [
        { text: this.$t('StudyActivity.activity_group'), value: 'activity_group_name' },
        { text: this.$t('StudyActivity.activity_sub_group'), value: 'activity_subgroup_name' }
      ]
    }
  },
  methods: {
    close () {
      this.$router.go(-1)
    }
  }
}
</script>
