<template>
  <SimpleFormDialog
    ref="dialog"
    :title="title"
    :open="open"
    @close="close"
    @submit="submit"
  >
    <template #body>
      <v-form ref="formRef">
        <v-row>
          <v-col>
            <v-autocomplete
              v-model="selectedPackage"
              :label="$t('CTStandardVersionsTable.sponsor_ct_package')"
              :items="packages"
              :rules="[formRules.required]"
              item-title="name"
              data-cy="sponsor-ct-package-dropdown"
              return-object
              clearable
              density="compact"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              :label="$t('CTStandardVersionsTable.ct_catalogue')"
              :model-value="
                selectedPackage ? selectedPackage.catalogue_name : undefined
              "
              density="compact"
              data-cy="ct-catalogue-field"
              disabled
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              :label="$t('CTStandardVersionsTable.cdisc_ct_package')"
              :model-value="
                selectedPackage ? selectedPackage.extends_package : undefined
              "
              density="compact"
              data-cy="cdisc-ct-package-field"
              disabled
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-textarea
              v-model="form.description"
              data-cy="description-field"
              :label="$t('_global.description')"
              density="compact"
              clearable
              rows="1"
              auto-grow
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
  </SimpleFormDialog>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import controlledTerminologyApi from '@/api/controlledTerminology'
import studyApi from '@/api/study'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'

const props = defineProps({
  standardVersion: {
    type: Object,
    default: null,
  },
  open: Boolean,
})
const emit = defineEmits(['close', 'save'])

const { t } = useI18n()
const formRules = inject('formRules')
const eventBusEmit = inject('eventBusEmit')
const studiesGeneralStore = useStudiesGeneralStore()

const dialog = ref()
const form = ref({})
const formRef = ref()
const packages = ref([])
const selectedPackage = ref(null)

const title = computed(() => {
  return props.standardVersion
    ? t('CTStandardVersionsForm.edit_title')
    : t('CTStandardVersionsForm.add_title')
})

watch(
  () => props.standardVersion,
  (value) => {
    if (value) {
      selectedPackage.value = value.ct_package
      form.value.description = value.description
    } else {
      selectedPackage.value = null
      form.value.description = ''
    }
  },
  { immediate: true }
)

function close() {
  form.value = {}
  selectedPackage.value = null
  emit('close')
}

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) {
    return
  }
  form.value.ct_package_uid = selectedPackage.value.uid
  try {
    if (!props.standardVersion) {
      await studyApi.createStudyStandardVersions(
        studiesGeneralStore.selectedStudy.uid,
        form.value
      )
      eventBusEmit('notification', {
        msg: t('CTStandardVersionsForm.add_success'),
      })
    } else {
      if (
        selectedPackage.value.uid === props.standardVersion.ct_package.uid &&
        props.standardVersion.description === form.value.description
      ) {
        eventBusEmit('notification', {
          type: 'info',
          msg: t('_global.no_changes'),
        })
        close()
        return
      }
      await studyApi.updateStudyStandardVersion(
        studiesGeneralStore.selectedStudy.uid,
        props.standardVersion.uid,
        form.value
      )
      eventBusEmit('notification', {
        msg: t('CTStandardVersionsForm.update_success'),
      })
    }
    emit('save')
    close()
  } finally {
    dialog.value.working = false
  }
}

controlledTerminologyApi.getSponsorPackages().then((resp) => {
  packages.value = resp.data
})
</script>
