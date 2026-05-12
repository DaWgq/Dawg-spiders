import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export function getWallpapers(params = {}) {
  return api.get('/wallpapers', { params })
}

export function getWallpaperDetail(wtId) {
  return api.get(`/wallpapers/${wtId}`)
}

export function getCategories() {
  return api.get('/categories')
}
