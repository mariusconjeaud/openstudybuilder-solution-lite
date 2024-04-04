<template>
<div>
  <validation-observer ref="observer">
    <validation-provider
      v-slot="{ errors }"
      :rules="`required|sameAs:${name}`"
      data-cy="sentence-case-name-class"
      >
      <v-row>
        <v-col>
          <v-text-field
            :label="$t('ActivityForms.name_sentence_case')"
            data-cy="sentence-case-name-field"
            v-model="sentenceCaseName"
            :error-messages="errors"
            dense
            clearable
            />
        </v-col>
      </v-row>
    </validation-provider>
  </validation-observer>
</div>
</template>

<script>
export default {
  props: {
    name: String,
    initialName: String
  },
  data () {
    return {
      sentenceCaseName: ''
    }
  },
  mounted () {
    if (this.initialName) {
      this.sentenceCaseName = this.initialName
    }
  },
  methods: {
    setSentenceCase () {
      if (this.name) {
        this.sentenceCaseName = this.name.toLowerCase()
      }
    }
  },
  watch: {
    name () {
      this.setSentenceCase()
    },
    initialName () {
      this.sentenceCaseName = this.initialName
    },
    sentenceCaseName (value) {
      this.$emit('input', value)
    }
  }
}
</script>
