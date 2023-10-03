<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('ActivityInstructionsView.title') }}
    <help-button :help-text="$t('_help.ActivityInstructionTable.general')" />
  </div>
  <activity-instruction-table />
</div>
</template>

<script>
import ActivityInstructionTable from '@/components/library/ActivityInstructionTable'
import HelpButton from '@/components/tools/HelpButton'

export default {
  components: {
    ActivityInstructionTable,
    HelpButton
  }
}
</script>
