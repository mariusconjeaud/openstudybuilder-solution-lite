<template>
  <div class="activity-summary-container">
    <table class="activity-summary-table">
      <tbody>
        <tr>
          <td>
            <div class="summary-label">
              {{ $t('_global.sentence_case_name') }}
            </div>
            <div class="summary-value">
              {{ activity.name_sentence_case || activity.name || '-' }}
            </div>
          </td>
          <td>
            <div class="summary-label">{{ $t('_global.start_date') }}</div>
            <div class="summary-value">
              {{
                activity.start_date
                  ? $filters.date(activity.start_date)
                  : 'None'
              }}
            </div>
          </td>
          <td>
            <div class="summary-label">{{ $t('_global.end_date') }}</div>
            <div class="summary-value">
              {{
                activity.end_date ? $filters.date(activity.end_date) : 'None'
              }}
            </div>
          </td>
          <td>
            <div class="summary-label">{{ $t('_global.status') }}</div>
            <div class="summary-value">
              <StatusChip v-if="activity.status" :status="activity.status" />
              <span v-else>-</span>
            </div>
          </td>
          <td>
            <div class="summary-label">{{ $t('_global.version') }}</div>
            <div class="summary-value">
              <v-select
                v-if="allVersions && allVersions.length"
                :items="allVersions"
                :model-value="activity.version"
                variant="outlined"
                density="compact"
                hide-details
                class="version-select"
                @update:model-value="$emit('version-change', $event)"
              ></v-select>
              <span v-else>{{ activity.version || '-' }}</span>
            </div>
          </td>
        </tr>
        <tr>
          <td>
            <div class="summary-label">{{ $t('_global.definition') }}</div>
            <div class="summary-value">{{ activity.definition || '-' }}</div>
          </td>
          <td v-if="showAbbreviation">
            <div class="summary-label">{{ $t('_global.abbreviation') }}</div>
            <div class="summary-value">{{ activity.abbreviation || '-' }}</div>
          </td>
          <td v-if="showLibrary">
            <div class="summary-label">{{ $t('_global.library') }}</div>
            <div class="summary-value">{{ activity.library_name || '-' }}</div>
          </td>
          <td v-if="showNciConceptId">
            <div class="summary-label">
              {{ $t('ActivityForms.nci_concept_id') || 'NCI Concept ID' }}
            </div>
            <div class="summary-value">
              <NCIConceptLink
                v-if="activity.nci_concept_id"
                :concept-id="activity.nci_concept_id"
              />
              <span v-else>-</span>
            </div>
          </td>
          <td v-if="showDataCollection">
            <div class="summary-label">
              {{ $t('activitySummary.dataCollection') }}
            </div>
            <div class="summary-value">
              {{ $filters.yesno(activity.is_data_collected) }}
            </div>
          </td>
          <td v-if="showAuthor">
            <div class="summary-label">{{ $t('_global.author') }}</div>
            <div class="summary-value">
              {{ activity.author_username || '-' }}
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import StatusChip from '@/components/tools/StatusChip.vue'
import NCIConceptLink from '@/components/tools/NCIConceptLink.vue'

useI18n() // Use i18n without assigning to a variable
defineEmits(['version-change'])

defineProps({
  activity: {
    type: Object,
    default: () => ({}),
  },
  allVersions: {
    type: Array,
    default: () => [],
  },
  showLibrary: {
    type: Boolean,
    default: true,
  },
  showNciConceptId: {
    type: Boolean,
    default: true,
  },
  showDataCollection: {
    type: Boolean,
    default: true,
  },
  showAbbreviation: {
    type: Boolean,
    default: true,
  },
  showAuthor: {
    type: Boolean,
    default: false,
  },
})
</script>

<!-- This needs to be set into a global place, color, fontsize etc -->
<style scoped>
.activity-summary-container {
  margin-bottom: 24px;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.activity-summary-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.activity-summary-table td {
  padding: 12px 16px;
  vertical-align: top;
  width: 20%;
  position: relative;
}

.summary-label {
  font-size: 14px;
  color: var(--semantic-system-brand, #001965);
  margin-bottom: 4px;
  font-weight: 400;
  text-transform: none;
}

.summary-value {
  font-weight: 700;
  font-size: 18px;
  line-height: 24px;
  letter-spacing: -0.02em;
  color: var(--semantic-system-brand, #001965);
  min-height: 24px;
}

.version-select {
  width: 120px;
}

.version-select :deep(.v-field__input),
.version-select :deep(.v-select__selection) {
  font-weight: 700;
  font-size: 18px;
  line-height: 24px;
  letter-spacing: -0.02em;
  color: var(--semantic-system-brand, #001965);
}

@media (max-width: 1200px) {
  .activity-summary-table,
  .activity-summary-table tbody,
  .activity-summary-table tr {
    display: block;
    width: 100%;
  }

  .activity-summary-table td {
    display: inline-block;
    width: 33.33%;
    box-sizing: border-box;
  }
}

@media (max-width: 768px) {
  .activity-summary-table td {
    width: 50%;
  }
}
</style>
