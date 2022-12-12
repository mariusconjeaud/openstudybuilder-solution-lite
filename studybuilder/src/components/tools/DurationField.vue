<template>
<div>
  <div :class="{ 'text_focused': text_focused, 'select_focused': select_focused }" class="d-flex">
    <validation-observer ref="observer">
      <validation-provider
        v-slot="{ errors }"
        :rules="durationRules"
        vid="manualInput"
        >
        <v-text-field
          data-cy="duration-value"
          class="value-selector"
          v-model="value[numericFieldName]"
          type="number"
          hide-details="auto"
          :error-messages="errors"
          :disabled="disabled"
          dense
          @focus="text_focused = true"
          @blur="text_focused = false"
          />
      </validation-provider>
    </validation-observer>
    <v-select
      data-cy="duration-unit"
      v-if="withUnit"
      class="unit-selector ml-4"
      :value="value[unitFieldName]"
      :placeholder="$t('DurationField.label')"
      :items="units"
      item-text="name"
      item-value="uid"
      return-object
      dense
      clearable
      hide-details="auto"
      @input="update(unitFieldName, $event)"
      :disabled="disabled"
      @focus="select_focused = true"
      @blur="select_focused = false"
      />
  </div>
  <div class="mt-1 v-input__control theme--light">
    <v-messages :value="text_focused||select_focused ? [hint]: []" />
  </div>
</div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters({
      units: 'studiesGeneral/units'
    }),
    durationRules () {
      let result = ''
      if (this.min_value !== undefined) {
        result += `min_value:${this.min}`
      }
      if (this.max_value !== undefined) {
        if (result !== '') {
          result += '|'
        }
        result += `max_value:${this.max}`
      }
      return result
    }
  },
  data () {
    return {
      select_focused: false,
      text_focused: false
    }
  },
  props: {
    value: Object,
    label: String,
    hint: String,
    errors: Array,
    numericFieldName: {
      type: String,
      default: () => 'duration_value'
    },
    unitFieldName: {
      type: String,
      default: () => 'duration_unit_code'
    },
    withUnit: {
      type: Boolean,
      default: true
    },
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      default: 100
    },
    step: {
      type: Number,
      default: 1
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    update (key, val) {
      if (val) {
        this.$emit('input', { ...this.value, [key]: { uid: val.uid, name: val.name } })
      } else {
        this.$emit('input', { ...this.value, [key]: undefined })
      }
    }
  }
}
</script>

<style>
.value-selector {
  max-width: 100px;
}
.unit-selector {
  max-width: 200px;
}
</style>
