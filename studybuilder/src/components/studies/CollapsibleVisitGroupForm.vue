<template>
<simple-form-dialog
  ref="form"
  :title="$t('CollapsibleVisitGroupForm.title')"
  @close="close"
  @submit="submit"
  :open="open"
  >
  <template v-slot:body>
    <v-alert
      border="left"
      type="warning"
      >
      {{ $t('CollapsibleVisitGroupForm.warning') }}
    </v-alert>
    <validation-observer ref="observer">
      <v-row>
        <v-col>
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-select
              v-model="visitTemplate"
              :items="visits"
              :label="$t('CollapsibleVisitGroupForm.visit_template')"
              item-text="visit_short_name"
              item-value="uid"
              :error-messages="errors"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </validation-observer>
  </template>
</simple-form-dialog>
</template>

<script>
import { mapGetters } from 'vuex'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog'
import studyEpochs from '@/api/studyEpochs'

export default {
  components: {
    SimpleFormDialog
  },
  props: {
    open: Boolean,
    visits: Array
  },
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      visitTemplate: null
    }
  },
  methods: {
    close () {
      this.$emit('close')
      this.visitTemplate = null
      this.$refs.observer.reset()
      this.$refs.form.working = false
    },
    async submit () {
      const valid = await this.$refs.observer.validate()
      if (!valid) {
        return
      }
      this.$refs.form.working = true
      const visitUids = this.visits.map(item => item.uid)
      await studyEpochs.createCollapsibleVisitGroup(this.selectedStudy.uid, visitUids, this.visitTemplate)
      this.$emit('created')
      this.close()
    }
  }
}
</script>
