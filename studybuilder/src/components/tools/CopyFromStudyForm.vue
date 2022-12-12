<template>
<v-card color="white">
  <v-card-title>
    <span class="dialog-title">{{ $t('StudyCopyForm.title') }}</span>
  </v-card-title>
  <v-card-text>
    <validation-observer ref="observer">
      <v-row class="mt-4">
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="atleastone:@studyId"
            vid="studyId"
            >
            <v-autocomplete
              v-model="study"
              :label="$t('StudyQuickSelectForm.study_id')"
              :items="studies"
              data-cy="study-id"
              item-text="study_id"
              item-value="uid"
              return-object
              :error-messages="errors"
              clearable
              />
          </validation-provider>
        </v-col>
        <v-col cols="6">
          <validation-provider
            v-slot="{ errors }"
            rules="atleastone:@studyAcronym"
            vid="studyAcronym"
            >
            <v-autocomplete
              v-model="study"
              :label="$t('StudyQuickSelectForm.study_acronym')"
              :items="studies"
              item-text="study_acronym"
              item-value="uid"
              return-object
              :error-messages="errors"
              clearable
              />
          </validation-provider>
        </v-col>
      </v-row>
      <v-spacer v-if="expand || expand2" class="distance"></v-spacer>
      <v-row>
        <v-col cols="6">
          <v-text-field
            v-if="study"
            v-model="study.study_status"
            readonly
            filled
            />
        </v-col>
      </v-row>
      <v-radio-group
        v-model="overwrite"
        hide-details
        :label="$t('StudyCopyForm.overwrite_content')"
      >
        <v-radio
          :label="$t('_global.yes')"
          data-cy="overwrite-yes"
          v-bind:value="true"
        ></v-radio>
        <v-radio
          :label="$t('_global.no')"
          data-cy="overwrite-no"
          v-bind:value="false"
        ></v-radio>
        </v-radio-group>
    </validation-observer>
  </v-card-text>
  <v-card-actions class="pb-4">
    <v-spacer />
    <v-btn
      class="secondary-btn"
      color="white"
      elevation="3"
      @click="close"
      >
      {{ $t('_global.cancel') }}
    </v-btn>
    <v-btn
      color="secondary"
      data-cy="ok-form"
      elevation="3"
      @click="select"
      >
      {{ $t('_global.ok') }}
    </v-btn>
  </v-card-actions>
</v-card>
</template>

<script>
import study from '@/api/study'
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters({
      selectedStudy: 'studiesGeneral/selectedStudy'
    })
  },
  data () {
    return {
      study: null,
      studies: [],
      expand: false,
      expand2: false,
      overwrite: false
    }
  },
  props: {
    component: String
  },
  methods: {
    close () {
      this.$emit('close')
    },
    select () {
      const form = {
        reference_study_uid: this.study.uid,
        component_to_copy: this.component,
        overwrite: this.overwrite
      }
      study.copyFromStudy(this.selectedStudy.uid, form).then(resp => {
        switch (this.component) {
          case 'high_level_study_design':
            this.$emit('apply', resp.data.current_metadata.high_level_study_design)
            break
          case 'study_intervention':
            this.$emit('apply', resp.data.current_metadata.study_intervention)
            break
          case 'study_population':
            this.$emit('apply', resp.data.current_metadata.study_population)
            break
        }
        this.close()
      })
    }
  },
  mounted () {
    study.getAll().then(resp => {
      this.studies = resp.data.items
    })
  }
}
</script>

<style scoped>
.distance {
  margin-bottom: 300px;
}
</style>
