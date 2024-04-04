<template>
<div>
  <div class="d-flex page-title">
    {{ $t('StudyArmsForm.study_arm') + ': ' + arm.name }} <v-chip :color="arm.arm_colour" small class="mt-2 ml-2"/>
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
          {{ $t('StudyArmsForm.arm_short_name') }}
        </v-col>
        <v-col cols="2">
          {{ arm.short_name }}
        </v-col>
      </v-row>
      <v-row v-if="arm.arm_type">
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyArmsForm.arm_type') }}
        </v-col>
        <v-col cols="2">
          {{ arm.arm_type.sponsor_preferred_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyArmsForm.randomisation_group') }}
        </v-col>
        <v-col cols="2">
          {{ arm.randomization_group }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyArmsForm.arm_code') }}
        </v-col>
        <v-col cols="2">
          {{ arm.code }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyArmsForm.planned_number') }}
        </v-col>
        <v-col cols="2">
          {{ arm.number_of_subjects }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyArmsForm.description') }}
        </v-col>
        <v-col cols="2">
          {{ arm.description }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyArmsForm.connected_branches') }}
        </v-col>
        <v-col cols="10">
          <v-data-table
            class="elevation-0"
            :headers="branchesHeaders"
            :items="arm.arm_connected_branch_arms ? arm.arm_connected_branch_arms : []"
            item-key="branch_arm_uid"
            light
            hide-default-footer
            >
            <template v-slot:item.name="{ item }">
              <router-link :to="{ name: 'StudyBranchArmOverview', params: { study_id: selectedStudy.uid, id: item.branch_arm_uid, root_tab: $route.params.root_tab } }">
                {{ item.name }}
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
import arms from '@/api/arms'
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  mounted () {
    arms.getStudyArm(this.$route.params.study_id, this.$route.params.id).then(resp => {
      this.arm = resp.data
    })
  },
  data () {
    return {
      arm: {},
      branchesHeaders: [
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyBranchArms.name'), value: 'name' },
        { text: this.$t('StudyBranchArms.short_name'), value: 'short_name' },
        { text: this.$t('StudyBranchArms.randomisation_group'), value: 'randomization_group' },
        { text: this.$t('StudyBranchArms.code'), value: 'code' },
        { text: this.$t('StudyBranchArms.description'), value: 'description' }
      ]
    }
  },
  methods: {
    close () {
      this.$router.push({ name: 'StudyStructure', params: { tab: this.$route.params.root_tab } })
    }
  }
}
</script>
