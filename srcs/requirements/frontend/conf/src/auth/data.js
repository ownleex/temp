import axiosInstance from "./instance"

const refreshData = async () => {
	try {
		const rawData = localStorage.getItem("data")
		if (!rawData) return
		const data = JSON.parse(rawData)
		if (!data?.id) return
		const response = await axiosInstance.get(`/users/api/player/${data.id}/`)
		if (response.data)
			localStorage.setItem("data", JSON.stringify(response.data))
	}
	catch {}
}

const getData = () => {
	try {
		const rawData = localStorage.getItem("data")
		return rawData ? JSON.parse(rawData) : null
	}
	catch {return null}
}

const removeData = () => {
	localStorage.removeItem("data")
	localStorage.removeItem("Atoken")
	localStorage.removeItem("Rtoken")
}

export { refreshData, getData, removeData }