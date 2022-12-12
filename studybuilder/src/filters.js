import Vue from 'vue'
import dataFormating from '@/utils/dataFormating'
import { DateTime } from 'luxon'

/*
** Return a human readable version of the given date string.
*/
Vue.filter('date', function (value) {
  return DateTime.fromISO(value).setLocale('en').toLocaleString(DateTime.DATETIME_MED)
})

/*
** Display a boolean value as a yes/no alternative.
*/
Vue.filter('yesno', dataFormating.yesno)

/*
** Remove square brackets from the given value.
*/
Vue.filter('stripBrackets', function (value) {
  return value.replaceAll(/\[|\]/g, '')
})

/*
** Display a list of terms
*/
Vue.filter('terms', function (value) {
  if (!value) {
    return ''
  }
  return value.map(item => item.name.sponsor_preferred_name).join(', ')
})

/*
** Display a list of objects names
*/
Vue.filter('names', dataFormating.names)

/*
** Display a list of lag times
*/
Vue.filter('lagTimes', dataFormating.lagTimes)

/*
** Display a list of substances
*/
Vue.filter('substances', dataFormating.substances)

/*
** Display a list of pharmacological classes
*/
Vue.filter('pharmacologicalClasses', dataFormating.pharmacologicalClasses)
