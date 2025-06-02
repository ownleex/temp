import axios from 'axios'
import { removeData } from './data.js'

const axiosInstance = axios.create({
	baseURL: `https://${location.host}`,
	withCredentials: true,
})

const rawAxios = axios.create({
	baseURL: `https://${location.host}`,
	withCredentials: true,
})


let isRefreshing = false
let refreshPromise = null

export const refreshAtoken = async (Rtoken, container) => {
	if (!Rtoken) return false
	if (isRefreshing) return refreshPromise
	isRefreshing = true
	refreshPromise = (async () => {
		try {
			let response
			if (container == "live_chat")
				response = await rawAxios.post('/live_chat/api/token/refresh/', { refresh: Rtoken })
			else if (container == "pong")
				response = await rawAxios.post('/pong/api/token/refresh/', { refresh: Rtoken })
			else
				response = await rawAxios.post('/users/api/token/refresh/', { refresh: Rtoken })
			if (response.data.access) {
				localStorage.setItem('Atoken', response.data.access)
				return true
			}
			return false
		}
		catch (error) {return false}
		finally {isRefreshing = false}
	})()
	return refreshPromise
}

const checkAPI = async (url) => {
	try {
		const containerStatus = await rawAxios.get(`/${url}/api/status/`)
		if (containerStatus.data.code != 1000) return false
		return true
	}
	catch {return false}
}

axiosInstance.interceptors.request.use(async (config) => {

	let Atoken = localStorage.getItem('Atoken')
	const Rtoken = localStorage.getItem('Rtoken')
	const isAuthAPI = config.url && (config.url.includes("/users/api/login/") ||
		config.url.includes("/users/api/register/") || config.url.includes("/users/api/auth-42/register/") ||
		config.url.includes("/users/api/auth-42/callback/?code=") || config.url.includes("/users/api/auth-42/status/") ||
		config.url.includes("/users/api/auth-42/complete/"))

	if (isAuthAPI)
		return config
	if (config.url && config.url.includes("/users/") && !(await checkAPI("users"))) throw new axios.Cancel()
	if (config.url && config.url.includes("/live_chat/") && !(await checkAPI("live_chat"))) throw new axios.Cancel()
	if (config.url && config.url.includes("/pong/") && !(await checkAPI("pong"))) throw new axios.Cancel()
	if (!Rtoken) {
		window.location.reload()
		return config
	}

	const istokenExpired = ((token) => {
		if (!token || !token.includes('.')) return true
		try {
			const payload = JSON.parse(atob(token.split('.')[1]))
			const expiry = payload.exp * 1000
			return Date.now() >= expiry
		}
		catch {return true}
	})

	if (istokenExpired(Rtoken)) {
		removeData()
		window.location.reload()
		return config
	}

	const container = config.url.split('/').filter(Boolean)

	if (istokenExpired(Atoken)) {
		const success = await refreshAtoken(Rtoken, container[0])
		if (!success) {
			removeData()
			return Promise.reject(new axios.Cancel("Access token refresh failed"))
		}
		Atoken = localStorage.getItem('Atoken')
	}
	if (Atoken)
		config.headers['Authorization'] = `Bearer ${Atoken}`

	return config
}, (error) => Promise.reject(error))

axiosInstance.interceptors.response.use((response) => response, async (error) => {
	const originalRequest = error.config

	if (error.response?.status === 401 && !originalRequest._retry) {
		originalRequest._retry = true
		
		const Rtoken = localStorage.getItem('Rtoken')
		const container = config.url.split('/').filter(Boolean)
		const refreshed = await refreshAtoken(Rtoken, container[0])
		
		if (refreshed) {
			const newAtoken = localStorage.getItem('Atoken')
			originalRequest.headers['Authorization'] = `Bearer ${newAtoken}`
			return axiosInstance(originalRequest)
		}
		else {
			removeData()
			window.location.reload()
			return Promise.reject(error)
		}
	}
    if (error.response?.status === 403 && originalRequest._retry) {
		removeData()
		window.location.reload()
	}
	return Promise.reject(error)
}
)

export default axiosInstance