import i18n from '@/plugins/i18n'

function lagTimes (value) {
  return value.map(item => `${item.sdtm_domain_label}: ${item.value} ${item.unit_label}`).join(', ')
}

function numericValue (value) {
  return `${value.value} ${value.unit_label}`
}

function pharmacologicalClasses (value) {
  return value.map(item => (item !== null && item.pclass_name) ? `${item.pclass_name} (${item.pclass_id})` : null).filter(pclass => pclass !== null).join(', ')
}

function yesno (value) {
  if (value === undefined || value === null) {
    return ''
  }
  return value ? i18n.t('_global.yes') : i18n.t('_global.no')
}

function substances (value) {
  return value.map(item => `${item.substance_name} (${item.substance_unii})`).join(', ')
}

function names (value) {
  return value.map(item => `${item.name}`).join(', ')
}

export default {
  lagTimes,
  numericValue,
  pharmacologicalClasses,
  substances,
  yesno,
  names
}
