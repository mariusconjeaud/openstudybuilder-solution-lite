
function prepareParameters (options, filters, sort, filtersUpdated) {
  const params = {
    page_number: (options.page),
    page_size: options.itemsPerPage,
    total_count: true
  }
  if (filtersUpdated) {
    /* Filters changed, reset page number */
    options.page = 1
  }
  if (filters !== undefined && filters !== '{}') {
    params.filters = filters
  }
  if (options.sortBy && options.sortBy.length !== 0 && sort !== undefined) {
    params.sort_by = `{"${options.sortBy[0]}":${!sort}}`
  }
  return params
}

export default {
  prepareParameters
}
