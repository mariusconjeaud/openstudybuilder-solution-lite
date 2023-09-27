<template>
<div class="px-4">
  <div class="page-title">{{ $t('ProtocolProcessView.title') }}</div>
  <v-card flat>
    <v-card-title class="text-h6">{{ $t('ProtocolProcessView.sub_title') }}</v-card-title>
    <v-card-text>
      <p>{{ $t('ProtocolProcessView.description') }}</p>
      <div class="d-flex flex-wrap align-center">
        <div v-for="(step, index) in protocol" :key="index" class="d-flex mt-4 text-center align-center">
          <v-menu offset-y v-if="step.items">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                color="primary"
                :class="step.padding ? step.padding : 'pa-6'"
                style="max-width: 150px"
                :data-cy=step.title
                v-bind="attrs"
                v-on="on"
                >
                {{ step.title }}
              </v-btn>
            </template>
            <v-list>
              <v-list-item
                v-for="(item, index) in step.items"
                :key="index"
                @click="navigate(item.to)"
                >
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <v-btn
            v-else-if="step.click"
            color="primary"
            :class="step.padding ? step.padding : 'pa-6'"
            style="max-width: 150px"
            :data-cy=step.title
            @click="step.click"
            >
            {{ step.title }}
          </v-btn>
          <v-btn
            v-else
            color="primary"
            :class="step.padding ? step.padding : 'pa-6'"
            style="max-width: 150px"
            :data-cy=step.title
            @click="navigate(step.to)"
            >
            {{ step.title }}
          </v-btn>
          <v-icon large v-if="index !== protocol.length - 1 && !step.separatorText" class="mx-4" color="secondary">
            mdi-arrow-right-bold-outline
          </v-icon>
          <span v-if="index !== protocol.length - 1 && step.separatorText" class="mx-6 secondary--text"><strong>{{ step.separatorText }}</strong></span>
        </div>
      </div>
    </v-card-text>
  </v-card>
  <confirm-dialog ref="confirm" :text-cols="5" :action-cols="6">
    <template v-slot:actions>
      <v-btn
        color="white"
        @click.native="openSelectStudyDialog"
        outlined
        class="mr-2"
        elevation="2"
        >
        {{ $t('_global.select_study') }}
      </v-btn>
      <v-btn
        color="white"
        @click.native="redirectToStudyTable"
        outlined
        elevation="2"
        >
        {{ $t('_global.add_study') }}
      </v-btn>
    </template>
  </confirm-dialog>
  <v-dialog
    v-model="showSelectForm"
    @keydown.esc="showSelectForm = false"
    persistent
    max-width="600px"
    >
    <study-quick-select-form @close="showSelectForm = false" @selected="goToNextUrl" />
  </v-dialog>
</div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import StudyQuickSelectForm from '@/components/studies/StudyQuickSelectForm'
import generalUtils from '@/utils/generalUtils'

export default {
  components: {
    ConfirmDialog,
    StudyQuickSelectForm
  },
  computed: {
    ...mapGetters({
      findMenuItemPath: 'app/findMenuItemPath',
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    const studyUid = generalUtils.extractStudyUidFromLocalStorage()
    return {
      protocol: [
        {
          title: this.$t('ProtocolProcessView.select_study'),
          click: this.showForm,
          separatorText: 'OR'
        },
        {
          title: this.$t('ProtocolProcessView.add_new_study'),
          to: { name: 'SelectOrAddStudy' }
        },
        {
          title: this.$t('ProtocolProcessView.study_structure'),
          items: [
            {
              title: this.$t('ProtocolProcessView.study_arms'),
              to: { name: 'StudyStructure', params: { tab: 'arms', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.study_epochs'),
              to: { name: 'StudyStructure', params: { tab: 'epochs', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.study_elements'),
              to: { name: 'StudyStructure', params: { tab: 'elements', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.study_visits'),
              to: { name: 'StudyStructure', params: { tab: 'visits', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.design_matrix'),
              to: { name: 'StudyStructure', params: { tab: 'design_matrix', study_id: studyUid } }
            }
          ]
        },
        {
          title: this.$t('ProtocolProcessView.study_purpose'),
          items: [
            {
              title: this.$t('ProtocolProcessView.study_title'),
              to: { name: 'StudyTitle', params: { study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.objectives'),
              to: { name: 'StudyPurpose', params: { tab: 'objectives', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.endpoints'),
              to: { name: 'StudyPurpose', params: { tab: 'endpoints', study_id: studyUid } }
            }
          ]
        },
        {
          title: this.$t('ProtocolProcessView.study_population'),
          items: [
            {
              title: this.$t('ProtocolProcessView.study_population'),
              to: { name: 'StudyPopulation', params: { study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.inclusion_criteria'),
              to: { name: 'StudySelectionCriteria', params: { tab: 'Inclusion Criteria', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.exclusion_criteria'),
              to: { name: 'StudySelectionCriteria', params: { tab: 'Exclusion Criteria', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.runin_criteria'),
              to: { name: 'StudySelectionCriteria', params: { tab: 'Run-in Criteria', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.randomisation_criteria'),
              to: { name: 'StudySelectionCriteria', params: { tab: 'Randomisation Criteria', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.dosing_criteria'),
              to: { name: 'StudySelectionCriteria', params: { tab: 'Dosing Criteria', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.withdrawal_criteria'),
              to: { name: 'StudySelectionCriteria', params: { tab: 'Withdrawal Criteria', study_id: studyUid } }
            }
          ]
        },
        {
          title: this.$t('ProtocolProcessView.study_interventions'),
          items: [
            {
              title: this.$t('ProtocolProcessView.overview'),
              to: { name: 'StudyInterventions', params: { tab: 'overview', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.study_compounds'),
              to: { name: 'StudyInterventions', params: { tab: 'study_compounds', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.study_compound_dosings'),
              to: { name: 'StudyInterventions', params: { tab: 'study_compound_dosings', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.other_interventions'),
              to: { name: 'StudyInterventions', params: { tab: 'other_interventions', study_id: studyUid } }
            }
          ]
        },
        {
          title: this.$t('ProtocolProcessView.schedules'),
          items: [
            {
              title: this.$t('ProtocolProcessView.activity_list'),
              to: { name: 'StudyActivities', params: { tab: 'list', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.detailed_flowchart'),
              to: { name: 'StudyActivities', params: { tab: 'detailed', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.protocol_flowchart'),
              to: { name: 'StudyActivities', params: { tab: 'protocol', study_id: studyUid } }
            },
            {
              title: this.$t('ProtocolProcessView.activity_instructions'),
              to: { name: 'StudyActivities', params: { tab: 'instructions', study_id: studyUid } }
            }
          ]
        }
      ],
      showSelectForm: false
    }
  },
  methods: {
    ...mapActions({
      addBreadcrumbsLevel: 'app/addBreadcrumbsLevel'
    }),
    async navigate (to) {
      this.nextUrl = to
      if (to.name !== 'SelectOrAddStudy' && !this.selectedStudy) {
        const options = {
          type: 'warning'
        }
        await this.$refs.confirm.open(this.$t('_global.no_study_selected'), options)
        return
      }
      this.goToNextUrl()
    },
    showForm () {
      this.showSelectForm = true
    },
    goToNextUrl () {
      if (!this.nextUrl) {
        this.nextUrl = { name: this.$route.name }
      }
      this.nextUrl.params = { study_id: generalUtils.extractStudyUidFromLocalStorage() }
      const resolved = this.$router.resolve(this.nextUrl)
      const [menuItem, menuSubItem] = this.findMenuItemPath('Studies', this.nextUrl.name)
      this.$store.commit('app/SET_SECTION', 'Studies')
      this.nextUrl = null
      if (menuItem) {
        this.addBreadcrumbsLevel({ text: menuItem.title, to: menuItem.url, index: 1 })
        if (menuSubItem) {
          this.addBreadcrumbsLevel({ text: menuSubItem.title, to: menuSubItem.url })
        }
      }
      document.location.href = resolved.href
    },
    openSelectStudyDialog () {
      this.$refs.confirm.cancel()
      this.showSelectForm = true
    },
    redirectToStudyTable () {
      this.$refs.confirm.cancel()
      this.$router.push({ name: 'SelectOrAddStudy' })
    }
  }
}
</script>

<style lang="scss">
.v-btn {
  &__content {
    width: 100% !important;
    white-space: normal !important;
  }
}
</style>
