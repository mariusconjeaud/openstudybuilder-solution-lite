<template>
<study-activity-selection-base-form
  :help-items="helpItems"
  :selection="selection"
  @submit="submit"
  @close="close"
  with-delete-action
  @remove="unselectItem"
  :open="open"
  >
  <template v-slot:body>
    <v-autocomplete
      v-model="form.flowchart_group"
      :label="$t('StudyActivityForm.flowchart_group')"
      :items="flowchartGroups"
      item-text="sponsor_preferred_name"
      return-object
      clearable
      class="border-top mt-4"
      />
    <v-checkbox
      v-model="form.deleteSelection"
      :color="form.deleteSelection ? 'error': ''"
      >
      <template v-slot:label>
        <span :class="{ 'error--text': form.deleteSelection }">
          {{ $t('StudyActivityBatchEditForm.delete_selection') }}
        </span>
      </template>
    </v-checkbox>
  </template>
</study-activity-selection-base-form>
</template>

<script>
import { bus } from '@/main'
import { mapGetters } from 'vuex'
import study from '@/api/study'
import StudyActivitySelectionBaseForm from './StudyActivitySelectionBaseForm'
import terms from '@/api/controlledTerminology/terms'

export default {
  components: {
    StudyActivitySelectionBaseForm
  },
  props: {
    selection: Array,
    open: Boolean
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      flowchartGroups: [],
      form: {},
      helpItems: []
    }
  },
  methods: {
    close () {
      this.form = {}
      this.$emit('close')
    },
    unselectItem (item) {
      this.$emit('remove', item)
    },
    async submit () {
      const data = []
      if (this.form.deleteSelection) {
        for (const item of this.selection) {
          data.push({
            method: 'DELETE',
            content: {
              study_activity_uid: item.study_activity_uid
            }
          })
        }
      }
      if (this.form.flowchart_group || this.form.note) {
        for (const item of this.selection) {
          const content = {
            note: this.form.note
          }
          if (this.form.flowchart_group) {
            content.soa_group_term_uid = this.form.flowchart_group.term_uid
          }
          data.push({
            method: 'PATCH',
            content: {
              study_activity_uid: item.study_activity_uid,
              content
            }
          })
        }
      }
      if (data.length) {
        study.studyActivityBatchOperations(this.selectedStudy.uid, data).then(() => {
          bus.$emit('notification', { type: 'success', msg: this.$t('StudyActivityBatchEditForm.update_success') })
          this.$emit('updated')
          this.close()
        })
      } else {
        this.close()
      }
    }
  },
  mounted () {
    terms.getByCodelist('flowchartGroups').then(resp => {
      this.flowchartGroups = resp.data.items
    })
  }
}
</script>

<style scoped>
.border-top {
  border-top: 1px solid var(--v-dfltBackground-darken1);
}
</style>
