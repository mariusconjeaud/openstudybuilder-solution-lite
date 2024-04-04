<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('SponsorView.title') }}
    <help-button :help-text="$t('_help.CtSponsorTable.general')" />
  </div>
  <sponsor-table
    :catalogue_name="$route.params.catalogue_name"
    />
</div>
</template>

<script>
import SponsorTable from '@/components/library/SponsorTable'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    SponsorTable,
    HelpButton
  }
}
</script>
