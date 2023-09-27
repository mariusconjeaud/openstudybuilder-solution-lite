<template>
<div>
  <v-dialog
    :value="open"
    @keydown.esc="cancel"
    scrollable
    persistent
    :max-width="maxWidth">
    <v-card data-cy="form-body" elevation="0">
      <v-card-title>
        <span class="dialog-title">{{ title }}</span>
        <help-button-with-panels
          :title="$t('_global.help')"
          :help-text="helpText"
          :items="helpItems"
          />
        <v-btn
          v-if="formUrl"
          color="secondary"
          class="ml-2"
          small
          @click="copyUrl"
          >
          {{  $t('_global.copy_link') }}
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <div>
          <slot name="body"></slot>
        </div>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <div>
          <slot name="actions"></slot>
        </div>
        <v-btn
          data-cy="cancel-button"
          class="secondary-btn"
          @click="cancel"
          :disabled="actionDisabled"
          outlined
          elevation="2"
          width="120px"
          >
          {{ $t('_global.cancel') }}
        </v-btn>
        <v-btn
          data-cy="save-button"
          color="secondary"
          @click="submit"
          :loading="working"
          :disabled="actionDisabled"
          v-if="!noSaving"
          elevation="2"
          width="120px"
          >
          {{ $t('_global.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <confirm-dialog ref="confirm" :text-cols="6" :action-cols="5" />
</div>
</template>

<script>
import ConfirmDialog from '@/components/tools/ConfirmDialog'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels'

export default {
  components: {
    ConfirmDialog,
    HelpButtonWithPanels
  },
  props: {
    title: String,
    helpItems: Array,
    helpText: {
      type: String,
      required: false
    },
    open: Boolean,
    maxWidth: {
      type: String,
      default: '800px'
    },
    noSaving: {
      type: Boolean,
      default: false
    },
    formUrl: String
  },
  data () {
    return {
      actionDisabled: false,
      working: false
    }
  },
  methods: {
    copyUrl () {
      navigator.clipboard.writeText(this.formUrl)
    },
    cancel () {
      this.$emit('close')
    },
    disableActions () {
      this.actionDisabled = true
    },
    enableActions () {
      this.actionDisabled = false
    },
    async confirm (message, options) {
      return await this.$refs.confirm.open(message, options)
    },
    submit () {
      this.$emit('submit')
    }
  }
}
</script>
