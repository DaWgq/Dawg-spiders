import { ref, computed } from 'vue'
import rawData from '../data/douban250.json'

export function useMovies() {
  const movies = ref(rawData)
  const searchQuery = ref('')
  const ratingRange = ref([8.0, 10.0])
  const yearRange = ref([1950, 2025])
  const selectedGenres = ref([])
  const selectedCountries = ref([])

  const availableGenres = computed(() => {
    const s = new Set()
    movies.value.forEach(m => m.genres.forEach(g => s.add(g)))
    return Array.from(s).sort()
  })

  const availableCountries = computed(() => {
    const s = new Set()
    movies.value.forEach(m => s.add(m.country))
    return Array.from(s).sort()
  })

  const filteredMovies = computed(() => {
    return movies.value.filter(m => {
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        if (!m.title.toLowerCase().includes(q) && !m.original_title.toLowerCase().includes(q) && !m.directors.some(d => d.toLowerCase().includes(q))) {
          return false
        }
      }
      if (m.rating < ratingRange.value[0] || m.rating > ratingRange.value[1]) return false
      if (m.year < yearRange.value[0] || m.year > yearRange.value[1]) return false
      if (selectedGenres.value.length && !selectedGenres.value.some(g => m.genres.includes(g))) return false
      if (selectedCountries.value.length && !selectedCountries.value.includes(m.country)) return false
      return true
    })
  })

  const ratingDistribution = computed(() => {
    const bins = {}
    for (let i = 80; i <= 97; i++) {
      const key = (i / 10).toFixed(1)
      bins[key] = 0
    }
    filteredMovies.value.forEach(m => {
      const key = m.rating.toFixed(1)
      if (bins[key] !== undefined) bins[key]++
    })
    return Object.entries(bins).map(([rating, count]) => ({ rating: parseFloat(rating), count }))
  })

  const yearDistribution = computed(() => {
    const map = {}
    filteredMovies.value.forEach(m => {
      map[m.year] = (map[m.year] || 0) + 1
    })
    return Object.entries(map)
      .map(([year, count]) => ({ year: parseInt(year), count }))
      .sort((a, b) => a.year - b.year)
  })

  const countryDistribution = computed(() => {
    const map = {}
    filteredMovies.value.forEach(m => {
      map[m.country] = (map[m.country] || 0) + 1
    })
    return Object.entries(map)
      .map(([country, count]) => ({ country, count }))
      .sort((a, b) => b.count - a.count)
  })

  function resetFilters() {
    searchQuery.value = ''
    ratingRange.value = [8.0, 10.0]
    yearRange.value = [1950, 2025]
    selectedGenres.value = []
    selectedCountries.value = []
  }

  return {
    movies,
    searchQuery,
    ratingRange,
    yearRange,
    selectedGenres,
    selectedCountries,
    availableGenres,
    availableCountries,
    filteredMovies,
    ratingDistribution,
    yearDistribution,
    countryDistribution,
    resetFilters,
  }
}
