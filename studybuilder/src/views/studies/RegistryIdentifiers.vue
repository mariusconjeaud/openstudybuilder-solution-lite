<template>
<div class="px-4">
  <div class="page-title d-flex align-center">
    {{ $t('StudyRegistryIdentifiersView.title') }} ({{ studyId }})
    <help-button :help-text="$t('_help.RegistryIdentifiersTable.general')" />
  </div>
  <registry-identifiers-summary />
  <comment-thread-list :topicPath="'/studies/' + selectedStudy.uid + '/registry_identifiers'" :isTransparent="false"></comment-thread-list>
</div>
</template>

<script>
import { studySelectedNavigationGuard } from '@/mixins/studies'
import RegistryIdentifiersSummary from '@/components/studies/RegistryIdentifiersSummary'
import HelpButton from '@/components/tools/HelpButton'
import CommentThreadList from '@/components/tools/CommentThreadList'

export default {
  mixins: [studySelectedNavigationGuard],
  components: {
    RegistryIdentifiersSummary,
    CommentThreadList,
    HelpButton
  }
}
</script>
