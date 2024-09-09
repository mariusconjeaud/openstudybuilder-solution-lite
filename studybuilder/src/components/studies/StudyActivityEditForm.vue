<template>
  <v-card bg-color="dfltBackground">
    <v-card-title class="d-flex align-center">
      <span class="dialog-title">{{ $t('StudyActivityEditForm.title') }}</span>
      <HelpButtonWithPanels :title="$t('_global.help')" :items="helpItems" />
    </v-card-title>
    <v-card-text class="mt-4">
      <div class="bg-white pa-4">
        <div class="d-flex">
          <v-text-field
            :label="$t('_global.library')"
            :model-value="library"
            disabled
            variant="filled"
            class="mr-2"
          />
          <v-text-field
            :label="$t('StudyActivity.activity_group')"
            :model-value="activity_group"
            disabled
            variant="filled"
            class="mr-2"
          />
          <v-text-field
            :label="$t('StudyActivity.activity_sub_group')"
            :model-value="activity_subgroup"
            disabled
            variant="filled"
            class="mr-2"
          />
          <v-text-field
            :label="$t('StudyActivity.activity')"
            :model-value="activity"
            disabled
            variant="filled"
          />
        </div>
        <v-form ref="observer">
          <v-autocomplete
            v-model="form.study_soa_group"
            :label="$t('StudyActivityForm.flowchart_group')"
            data-cy="flowchart-group"
            :items="flowchartGroups"
            item-title="name.sponsor_preferred_name"
            return-object
            :rules="[formRules.required]"
            clearable
          />
        </v-form>
      </div>
    </v-card-text>
    <v-card-actions class="pr-6 pb-6">
      <v-spacer />
      <v-btn
        class="secondary-btn"
        variant="outlined"
        elevation="2"
        width="120px"
        @click="close"
      >
        {{ $t('_global.cancel') }}
      </v-btn>
      <v-btn
        color="secondary"
        variant="flat"
        elevation="2"
        width="120px"
        :loading="working"
        @click="submit"
      >
        {{ $t('_global.save') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import study from '@/api/study'
import terms from '@/api/controlledTerminology/terms'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels.vue'

const { t } = useI18n()
const eventBusEmit = inject('eventBusEmit')
const formRules = inject('formRules')
const props = defineProps({
  studyActivity: {
    type: Object,
    default: undefined,
  },
})
const emit = defineEmits(['close', 'updated'])

const studiesGeneralStore = useStudiesGeneralStore()

const flowchartGroups = ref([])
const form = ref({})
const working = ref(false)
const observer = ref()

const helpItems = []

const library = computed(() => {
  return props.studyActivity && props.studyActivity.activity
    ? props.studyActivity.activity.library_name
    : ''
})
const activity_group = computed(() => {
  return props.studyActivity &&
    props.studyActivity.study_activity_group &&
    props.studyActivity.study_activity_group.activity_group_name
    ? props.studyActivity.study_activity_group.activity_group_name
    : ''
})
const activity_subgroup = computed(() => {
  return props.studyActivity &&
    props.studyActivity.study_activity_subgroup &&
    props.studyActivity.study_activity_subgroup.activity_subgroup_name
    ? props.studyActivity.study_activity_subgroup.activity_subgroup_name
    : ''
})
const activity = computed(() => {
  return props.studyActivity ? props.studyActivity.activity.name : ''
})

watch(
  () => props.studyActivity,
  (value) => {
    if (value) {
      study
        .getStudyActivity(
          studiesGeneralStore.selectedStudy.uid,
          value.study_activity_uid
        )
        .then((resp) => {
          form.value = { ...resp.data }
          form.value.study_soa_group.name = {
            sponsor_preferred_name: form.value.study_soa_group.soa_group_name,
          }
        })
    } else {
      form.value = {}
    }
  },
  { immediate: true }
)

onMounted(() => {
  terms.getByCodelist('flowchartGroups').then((resp) => {
    flowchartGroups.value = resp.data.items
  })
})

function close() {
  working.value = false
  form.value = {}
  observer.value.reset()
  emit('close')
}

async function submit() {
  const { valid } = await observer.value.validate()
  if (!valid) {
    return
  }
  working.value = true
  const data = {
    soa_group_term_uid: form.value.study_soa_group.term_uid,
  }
  study
    .updateStudyActivity(
      props.studyActivity.study_uid,
      props.studyActivity.study_activity_uid,
      data
    )
    .then(
      () => {
        eventBusEmit('notification', {
          type: 'success',
          msg: t('StudyActivityEditForm.update_success'),
        })
        emit('updated')
        close()
      },
      () => {
        working.value = false
      }
    )
}
</script>
