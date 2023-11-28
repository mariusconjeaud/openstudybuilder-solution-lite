<template>
<div>
  <div class="d-flex page-title">
    {{ $t('StudyCohorts.study_cohort') + ': ' + cohort.name }} <v-chip :color="cohort.colour_code" small class="mt-2 ml-2"/>
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
          {{ $t('StudyCohorts.cohort_short_name') }}
        </v-col>
        <v-col cols="2">
          {{ cohort.short_name }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyCohorts.cohort_code') }}
        </v-col>
        <v-col cols="2">
          {{ cohort.code }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyCohorts.number_of_subjects') }}
        </v-col>
        <v-col cols="2">
          {{ cohort.number_of_subjects }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyCohorts.description') }}
        </v-col>
        <v-col cols="2">
          {{ cohort.description }}
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyCohorts.connected_arms') }}
        </v-col>
        <v-col cols="10">
          <v-data-table
            class="elevation-0"
            :headers="armsHeaders"
            :items="cohort.arm_roots"
            item-key="arm_uid"
            light
            hide-default-footer
            >
            <template v-slot:item.name="{ item }">
              <router-link :to="{ name: 'StudyArmOverview', params: { study_id: selectedStudy.uid, id: item.arm_uid } }">
                {{ item.name }}
              </router-link>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2" class="font-weight-bold">
          {{ $t('StudyCohorts.connected_branches') }}
        </v-col>
        <v-col cols="10">
          <v-data-table
            class="elevation-0"
            :headers="branchesHeaders"
            :items="cohort.branch_arm_roots"
            item-key="branch_arm_uid"
            light
            hide-default-footer
            >
            <template v-slot:item.name="{ item }">
              <router-link :to="{ name: 'StudyBranchArmOverview', params: { study_id: selectedStudy.uid, id: item.branch_arm_uid } }">
                {{ item.name }}
              </router-link>
            </template>
            <template v-slot:item.arm_root.name="{ item }">
              <router-link :to="{ name: 'StudyArmOverview', params: { study_id: selectedStudy.uid, id: item.arm_root.arm_uid } }">
                {{ item.arm_root.name }}
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
    arms.getStudyCohort(this.$route.params.study_id, this.$route.params.id).then(resp => {
      this.cohort = resp.data
    })
  },
  data () {
    return {
      cohort: {},
      armsHeaders: [
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyArmsTable.type'), value: 'arm_type.sponsor_preferred_name', width: '7%' },
        { text: this.$t('StudyArmsTable.name'), value: 'name' },
        { text: this.$t('StudyArmsTable.short_name'), value: 'short_name' },
        { text: this.$t('StudyArmsTable.randomisation_group'), value: 'randomization_group' },
        { text: this.$t('StudyArmsTable.code'), value: 'code' },
        { text: this.$t('StudyArmsTable.description'), value: 'description' }
      ],
      branchesHeaders: [
        { text: '#', value: 'order', width: '5%' },
        { text: this.$t('StudyBranchArms.arm_name'), value: 'arm_root.name', historyHeader: 'arm_root_uid' },
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
      this.$router.push({ name: 'StudyStructure', params: { tab: 'cohorts' } })
    }
  }
}
</script>
