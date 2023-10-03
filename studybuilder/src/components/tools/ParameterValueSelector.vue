<template>
<div>
  <div class="mt-2 mb-8">
    <div class="mb-2 secondary--text text-h6">
      <template v-if="previewText">{{ previewText }}</template>
      <template v-else>{{ $t('ParameterValueSelector.preview') }}</template>
    </div>
    <v-card flat class="parameterBackground">
      <v-card-text>
        <n-n-parameter-highlighter
          :name="namePreview"
          :show-prefix-and-postfix="false"
          :parameters="parameters"
          edition-mode
          />
      </v-card-text>
    </v-card>
  </div>
  <div :class="color" v-if="stacked">
    <v-row v-for="(parameter, index) in parameters"
            :key="index"
            no-gutters
            dense
            cols="3"
            >
      <v-row class="align-start">
        <v-col cols="10">
          <validation-provider
            v-slot="{ errors }"
            :vid="`value-${index}`"
            :name="`value-${index}`"
            :rules="!loadParameterValuesFromTemplate ? `requiredIfNotNA:${parameter.skip}` : ''"
            >
            <v-text-field
              v-if="parameter.name === 'NumericValue'"
              v-model="parameter.selectedValues"
              :label="parameter.name"
              :error-messages="errors"
              :disabled="disabled || parameter.skip"
              type="number"
              @input="update"
              />
            <v-textarea
              v-else-if="parameter.name === 'TextValue'"
              v-model="parameter.selectedValues"
              :label="parameter.name"
              :error-messages="errors"
              :disabled="disabled || parameter.skip"
              rows="1"
              @input="update"
              auto-grow
              />
            <multiple-select
              v-else
              v-model="parameter.selectedValues"
              :label="parameter.name"
              :items="parameter.terms"
              :errors="errors"
              return-object
              :disabled="disabled || parameter.skip"
              shorter-preview
              @input="update"
              />
          </validation-provider>
        </v-col>
        <v-col cols="2">
          <validation-provider
            v-if="!loadParameterValuesFromTemplate"
            v-slot="{ errors }"
            :name="`skip-${index}`"
            :vid="`skip-${index}`"
            >
            <v-btn
              icon
              class="ml-4"
              @click="clearSelection(parameter)"
              :error-messages="errors"
              :disabled="disabled"
            >
              <v-icon v-if="!parameter.skip">mdi-eye-outline</v-icon>
              <v-icon v-else>mdi-eye-off-outline</v-icon>
            </v-btn>
          </validation-provider>
        </v-col>
      </v-row>
      <v-row v-if="parameter.selectedValues && parameter.selectedValues.length > 1 && parameter.name !== 'NumericValue' && parameter.name !== 'TextValue'">
        <v-col
          cols="8"
          class="pl-2"
          >
          <validation-provider
            v-slot="{ errors }"
            rules="required"
            >
            <v-select
              v-model="parameter.selectedSeparator"
              :label="$t('ParameterValueSelector.separator')"
              :items="separators"
              dense
              clearable
              :error-messages="errors"
              :disabled="parameter.skip"
              @input="update"
              />
          </validation-provider>
        </v-col>
      </v-row>
    </v-row>
  </div>
  <div :class="color" v-else>
    <v-row>
      <v-col v-for="(parameter, index) in parameters"
             :key="index"
             no-gutters
             dense
             cols="3"
             >
        <v-row class="align-start">
          <v-col cols="10">
            <validation-provider
              v-slot="{ errors }"
              :vid="`value-${index}`"
              :name="`value-${index}`"
              :rules="!loadParameterValuesFromTemplate ? `requiredIfNotNA:${parameter.skip}` : ''"
              >
              <v-text-field
                v-if="parameter.name === 'NumericValue'"
                v-model="parameter.selectedValues"
                :label="parameter.name"
                :error-messages="errors"
                :disabled="parameter.skip"
                type="number"
                dense
                @input="update"
                />
              <v-textarea
                v-else-if="parameter.name === 'TextValue'"
                v-model="parameter.selectedValues"
                :label="parameter.name"
                :error-messages="errors"
                :disabled="parameters[index].skip"
                :rows="1"
                dense
                @input="update"
                auto-grow
                />
              <multiple-select
                :data-cy="parameter.name"
                v-else
                v-model="parameter.selectedValues"
                :label="parameter.name"
                :items="parameter.terms"
                :errors="errors"
                return-object
                :disabled="parameter.skip"
                shorter-preview
                @input="update"
                />
            </validation-provider>
          </v-col>
          <v-col cols="2">
            <validation-provider
              v-slot="{ errors }"
              :name="`skip-${index}`"
              :vid="`skip-${index}`"
              >
              <v-btn
                icon
                class=" ml-n4"
                @click="clearSelection(parameter)"
                :error-messages="errors"
                :title="$t('ParameterValueSelector.na_tooltip')"
              >
                <v-icon v-if="!parameter.skip">mdi-eye-outline</v-icon>
                <v-icon v-else>mdi-eye-off-outline</v-icon>
              </v-btn>
            </validation-provider>
          </v-col>
        </v-row>
        <v-row v-if="parameter.selectedValues && parameter.selectedValues.length > 1 && parameter.name !== 'NumericValue' && parameter.name !== 'TextValue'">
          <v-col
            cols="8"
            class="pl-2"
            >
            <validation-provider
              v-slot="{ errors }"
              rules="required"
              >
              <v-select
                v-model="parameter.selectedSeparator"
                :label="$t('ParameterValueSelector.separator')"
                :items="separators"
                dense
                clearable
                :error-messages="errors"
                :disabled="parameter.skip"
                @input="update"
                />
            </validation-provider>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>

  <template v-if="withUnformattedVersion">
    <p class="secondary--text text-h6">{{ unformattedTextLabel }}</p>
    <div class="pa-4 parameterBackground">
      {{ namePlainPreview }}
    </div>
  </template>
</div>
</template>

<script>
import constants from '@/constants/parameters'
import templateParameters from '@/utils/templateParameters'
import MultipleSelect from '@/components/tools/MultipleSelect'
import NNParameterHighlighter from '@/components/tools/NNParameterHighlighter'
import { parameterValuesMixin } from '@/mixins/parameterValues'
import templateParameterTypes from '@/api/templateParameterTypes'

export default {
  mixins: [parameterValuesMixin],
  components: {
    MultipleSelect,
    NNParameterHighlighter
  },
  props: {
    value: Array,
    template: String,
    color: {
      type: String,
      default: 'white'
    },
    errorMessages: {
      type: Array,
      required: false
    },
    loadParameterValuesFromTemplate: {
      type: Boolean,
      default: false
    },
    previewText: String,
    stacked: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    withUnformattedVersion: {
      type: Boolean,
      default: true
    },
    unformattedLabel: {
      type: String,
      required: false
    }
  },
  computed: {
    namePreview () {
      return this.cleanName(this.getNamePreview())
    },
    namePlainPreview () {
      let namePreview = this.cleanName(this.getNamePreview())
      namePreview = namePreview.replaceAll('</li>', '; ').replaceAll('<li>', ' ')
      if (namePreview !== undefined) {
        const tag = new DOMParser().parseFromString(namePreview, 'text/html')
        if (tag.documentElement.textContent) {
          return tag.documentElement.textContent.replaceAll(/\[|\]/g, '')
        }
      }
      return ''
    },
    unformattedTextLabel () {
      return this.unformattedLabel ? this.unformattedLabel : this.$t('_global.plain_text_version')
    }
  },
  data () {
    return {
      parameters: [],
      separators: [' and ', ' or ', ' and/or ']
    }
  },
  created () {
    // Force skip property initialization to avoid a strange side
    // effect with selection clearing and textvalue fields...
    for (const parameter of this.value) {
      if (parameter.skip === undefined) {
        this.$set(parameter, 'skip', false)
      }
    }
  },
  mounted () {
    this.parameters = [...this.value]
  },
  methods: {
    clearSelection (parameter) {
      this.$set(parameter, 'selectedValues', [])
      this.$set(parameter, 'selectedSeparator', null)
      this.$set(parameter, 'skip', !parameter.skip)
      this.update()
    },
    cleanName (value) {
      const rules = {
        '([])': '[]',
        '  ': ' ',
        '[] []': '[][]',
        '[] ([': '[]([',
        '[) []': '])[]',
        '] and []': '][]',
        '[] and [': '[][',
        '], []': '][]',
        '[], [': '[][',
        '] or []': '][]',
        '[] or [': '[][',
        '] []': '][]',
        '[] [': '[]['
      }
      for (const original of Object.keys(rules)) {
        value = value.replace(original, rules[original])
      }
      return value.trim()
    },
    getNamePreview (hideEmptyParams) {
      if (!this.template) {
        return ''
      }
      if (!this.parameters.length) {
        return this.template
      }
      let result = ''
      let paramIndex = 0
      let inParam = false
      for (const c of this.template) {
        if (c === '[') {
          inParam = true
        } else if (c === ']') {
          if (paramIndex < this.parameters.length) {
            if (this.parameters[paramIndex].selectedValues && this.parameters[paramIndex].selectedValues.length) {
              if (this.parameters[paramIndex].name === constants.NUM_VALUE || this.parameters[paramIndex].name === constants.TEXT_VALUE) {
                result += '[' + this.parameters[paramIndex].selectedValues + ']'
              } else {
                const valueNames = this.parameters[paramIndex].selectedValues.map(v => v.name)
                const concatenation = (this.parameters[paramIndex].selectedSeparator)
                  ? valueNames.join(this.parameters[paramIndex].selectedSeparator)
                  : valueNames.join(' ')
                result += `[${concatenation}]`
              }
            } else if (this.parameters[paramIndex].skip) {
              result += hideEmptyParams ? '' : '[]'
            } else {
              result += `[${this.parameters[paramIndex].name}]`
            }
          }
          paramIndex++
          inParam = false
        } else if (!inParam) {
          result += c
        }
      }
      return result
    },
    update () {
      this.$emit('input', this.parameters)
    }
  },
  watch: {
    /*
    ** Here we delay the execution of the watcher to avoid unexpected behaviour when the user leaves his finger pressed
    ** on a key for example.
    */
    async template (value) {
      if (this.updatingParameters) {
        return
      }
      setTimeout(async () => {
        if (value !== this.template) {
          return
        }
        this.updatingParameters = true
        if (this.loadParameterValuesFromTemplate && value) {
          this.parameters = []
          const extractedParams = templateParameters.getTemplateParametersFromTemplate(value)
          if (extractedParams.length !== this.value.length) {
            this.$emit('input', [])
          }
          for (const param of extractedParams) {
            const resp = await templateParameterTypes.getTerms(param)
            this.parameters.push({
              name: param,
              terms: resp.data
            })
          }
          if (this.value.length) {
            this.value.forEach((param, index) => {
              if (param.selectedValues) {
                this.$set(this.parameters[index], 'selectedValues', param.selectedValues)
              }
              if (param.selectedSeparator) {
                this.$set(this.parameters[index], 'selectedSeparator', param.selectedSeparator)
              }
            })
          }
        }
        this.updatingParameters = false
      }, 100)
    },
    value (newVal) {
      if (newVal) {
        this.parameters = [...newVal]
      }
    }
  }
}
</script>
