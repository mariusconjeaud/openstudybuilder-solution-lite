<template>
  <PackageTimelines
    ref="timelines"
    :catalogue-name="props.catalogueName"
    :package-name="props.packageName"
    sponsor
    @catalogue-changed="updateUrl"
    @package-changed="updateUrl"
    @add-package="showCreationForm = true"
  >
    <template #default="{ catalogue_name, selectedPackage }">
      <CodelistTable
        v-if="!_isEmpty(timelines.packages)"
        ref="table"
        :catalogue="catalogue_name"
        :package="selectedPackage"
        sponsor
        read-only
        column-data-resource="ct/codelists"
        :display-table-toolbar="false"
        :display-row-actions="false"
      >
        <template #beforeToolbar>
          <div v-if="selectedPackage" class="d-flex align-center my-2">
            {{ $t('SponsorCTPackagesTable.date') }}
            {{ selectedPackage.effective_date }}
            <v-spacer />
            {{ $t('SponsorCTPackagesTable.connected_to') }}
            {{ selectedPackage.extends_package }}
            <v-spacer />
          </div>
        </template>
      </CodelistTable>
      <v-card v-else class="pa-4">
        <v-card-text class="text-center">
          <p>{{ $t('SponsorCTPackagesTable.no_package_yet') }}</p>
          <v-btn color="primary" class="mt-4" @click="showCreationForm = true">
            {{ $t('SponsorCTPackagesTable.create_first_one') }}
          </v-btn>
        </v-card-text>
      </v-card>
    </template>
  </PackageTimelines>
  <SponsorCTPackageForm
    :open="showCreationForm"
    @close="closeCreationForm"
    @created="timelines.fetchPackages()"
  />
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import _isEmpty from 'lodash/isEmpty'
import CodelistTable from './CodelistTable.vue'
import PackageTimelines from './PackageTimelines.vue'
import SponsorCTPackageForm from './SponsorCTPackageForm.vue'

const props = defineProps({
  catalogueName: {
    type: String,
    default: null,
  },
  packageName: {
    type: String,
    default: '',
  },
})
const router = useRouter()

const showCreationForm = ref(false)
const table = ref()
const timelines = ref()

function updateUrl(catalogueName, pkg) {
  router.push({
    name: 'SponsorCtPackages',
    params: {
      catalogue_name: catalogueName,
      package_name: pkg ? pkg.name : null,
    },
  })
  table.value.refresh()
}

function closeCreationForm() {
  showCreationForm.value = false
}
</script>
