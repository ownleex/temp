import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js'
import { AmbientLight, DirectionalLight } from 'three'

export const setAll = (scene, state, groupName, groupScore) => {

	const floor = setFloor(scene)
	const fog = setFog(scene)
	const light = setLight(scene)
	if (state != "play") return {floor, fog, light}
	//const line = setLine()
	const border = setBorder(scene)
	const bscreen = setBScreen(scene)
	const paddle = setPaddle(scene)
	const wall = setWall(scene)
	const ball = setBall(scene)
	const names = setNames(groupName, scene)
	const score = setScore(groupScore, scene)

	//line.cubes.forEach(cube => scene.add(cube))
	return {floor, fog, light, paddle, wall, ball, border, bscreen, names, score}
}

const setFloor = (scene) => {
	const geometry = new THREE.PlaneGeometry(1000, 1000)
	const material = new THREE.MeshStandardMaterial({color: 0x7fdce2})
	const floor = new THREE.Mesh(geometry, material)
	floor.position.set(0, 0, -1.5)
	floor.receiveShadow = true
	scene.add(floor)
	return floor
}

const setFog = (scene) => {
	const bg = new THREE.Color(0x326e72)
	const fog = new THREE.Fog(0x326e72, 15, 150)
	scene.background = bg
	scene.fog = fog
	return {bg, fog}
}

const setLine = () => {
	let cubes = [], geometry, material, cube, n = 19
	for (let i = 1; i <= n; i++) {
		geometry = new THREE.PlaneGeometry(0.8, 0.5)
		material = new THREE.MeshBasicMaterial({color: 0x2a484a})
		cube = new THREE.Mesh(geometry, material)
		cube.position.set(17 - (i * ((17 * 2) / n)), 0, -1.4)
		cube.rotateX(-Math.PI * 0.5)
		cubes.push(cube)
	}
	return {cubes, n}
}

const setBorder = (scene) => {
	const geometry = new THREE.TubeGeometry( new THREE.CatmullRomCurve3([
		new THREE.Vector3(-15, 0, 0),
		new THREE.Vector3(-15, 0, 20),
		new THREE.Vector3(15, 0, 20),
		new THREE.Vector3(15, 0, 0),
	], true), 64, 1, 16, false)
	const material = new THREE.MeshStandardMaterial({color: 0xDDDDDD})
	const border = new THREE.Mesh(geometry, material)
	border.position.set(35, 31, -5)
	scene.add(border)
	return border
}

const setBScreen = (scene) => {
	const geometry1 = new THREE.PlaneGeometry(34, 12)
	const geometry2 = new THREE.PlaneGeometry(32, 2)
	const geometry3 = new THREE.PlaneGeometry(26, 2.5)
	const material = new THREE.MeshStandardMaterial({color: 0x000000, side: THREE.DoubleSide})
	const bscreen1 = new THREE.Mesh(geometry1, material)
	const bscreen2 = new THREE.Mesh(geometry2, material)
	const bscreen3 = new THREE.Mesh(geometry3, material)
	bscreen1.position.set(35, 32, 7)
	bscreen2.position.set(35, 32, 14)
	bscreen3.position.set(35, 32, 16)
	bscreen1.rotateX(-Math.PI / 2)
	bscreen2.rotateX(-Math.PI / 2)
	bscreen3.rotateX(-Math.PI / 2)
	scene.add(bscreen1, bscreen2, bscreen3)
	return {bscreen1, bscreen2, bscreen3}
}

const setLight = (scene) => {
	const ambientLight = new AmbientLight(0xffffff, 0.5)
	const dirLight = new DirectionalLight(0xffffff, 1)
	dirLight.position.set(50, 30, 20)
	dirLight.target.position.set(35, 15, 0)
	dirLight.castShadow = true
	dirLight.shadow.bias = -0.0005
	dirLight.shadow.mapSize.width = 1024
	dirLight.shadow.mapSize.height = 1024


	const d = 60
	dirLight.shadow.camera.left = -d
	dirLight.shadow.camera.right = d
	dirLight.shadow.camera.top = d
	dirLight.shadow.camera.bottom = -d
	dirLight.shadow.camera.near = 1
	dirLight.shadow.camera.far = 150

	scene.add(ambientLight, dirLight, dirLight.target)
	return {ambientLight, dirLight}
}

const setPaddle = (scene) => {
	const geometry = new THREE.BoxGeometry(1, 5, 1)
	const material = new THREE.MeshStandardMaterial({color: 0x2a484a})
	const paddleL = new THREE.Mesh(geometry, material)
	paddleL.castShadow = true
	paddleL.receiveShadow = true
	const paddleR = paddleL.clone()
	scene.add(paddleL, paddleR)
	return {paddleL, paddleR}
}

const setWall = (scene) => {
	const geometry = new RoundedBoxGeometry(75, 1, 3, 5, 0.5)
	const material = new THREE.MeshStandardMaterial({color: 0xDDDDDD})
	const wallL = new THREE.Mesh(geometry, material)
	wallL.castShadow = true
	wallL.receiveShadow = true
	const wallR = wallL.clone()
	wallL.position.set(35, -0.5, 0)
	wallR.position.set(35, 30.5, 0)
	scene.add(wallL, wallR)
	return {wallL, wallR}
}

const setBall = (scene) => {
	const geometry = new RoundedBoxGeometry(1, 1, 1, 5, 0.5)
	const material = new THREE.MeshStandardMaterial({color: 0xffaa00})
	const ball = new THREE.Mesh(geometry, material)
	ball.castShadow = true
	ball.receiveShadow = true
	scene.add(ball)
	return ball
}

const setScore = (groupScore, scene) => {
	const canvas = document.createElement('canvas')
	canvas.width = 512
	canvas.height = 512
	const ctx = canvas.getContext('2d')
	ctx.translate(0, canvas.height)
    ctx.scale(1, -1)
	ctx.font = 'bold 40px "Courier New", monospace'
	ctx.fillStyle = 'white'
	ctx.textAlign = 'center'
	ctx.textBaseline = 'middle'
	const s1 = (groupScore && groupScore.score1 != undefined ? `${groupScore.score1}` : "0")
	const s2 = (groupScore && groupScore.score2 != undefined ? `${groupScore.score2}` : "0")
	const text = `${s1} - ${s2}`
	ctx.fillText(text, canvas.width / 2, canvas.height / 2)
	const texture = new THREE.Texture(canvas)
	texture.flipY = false
	texture.premultiplyAlpha = false
	texture.needsUpdate = true
	const material = new THREE.MeshBasicMaterial({
		map: texture, transparent: true, side: THREE.DoubleSide})
	const geometry = new THREE.PlaneGeometry(50, 50)
	const textMesh = new THREE.Mesh(geometry, material)
	textMesh.position.set(35, 30, 7)
	textMesh.rotateX(Math.PI / 2)
	scene.add(textMesh)
	return (textMesh)
}

export const updateScore = (newScore, scene, objects) => {
	scene.remove(objects.score)
	if (objects.score.material.map) {
		objects.score.material.map.dispose()
	}
	objects.score.geometry.dispose()
	objects.score.material.dispose()
	const newScoreMesh = setScore(newScore, scene)
	objects.score = newScoreMesh
}


const setNames = (groupName, scene) => {
	const canvas = document.createElement('canvas')
	canvas.width = 512
	canvas.height = 512
	const ctx = canvas.getContext('2d')
	ctx.translate(0, canvas.height)
    ctx.scale(1, -1)
	ctx.font = 'bold 20px "Courier New", monospace'
	ctx.fillStyle = 'white'
	ctx.textAlign = 'center'
	ctx.textBaseline = 'middle'
	const text = (groupName && groupName.name1 && groupName.name2
		? `${groupName.name1} vs ${groupName.name2}`
		: "...   vs   ...")
	ctx.fillText(text, canvas.width / 2, canvas.height / 2)
	const texture = new THREE.Texture(canvas)
	texture.flipY = false
	texture.premultiplyAlpha = false
	texture.needsUpdate = true
	const material = new THREE.MeshBasicMaterial({
		map: texture, transparent: true, side: THREE.DoubleSide})
	const geometry = new THREE.PlaneGeometry(50, 50)
	const textMesh = new THREE.Mesh(geometry, material)
	textMesh.position.set(35, 30, 14)
	textMesh.rotateX(Math.PI / 2)
	scene.add(textMesh)
	return (textMesh)
}

export const updateName = (newName, scene, objects) => {
	scene.remove(objects.names)
	if (objects.names.material.map) {
		objects.names.material.map.dispose()
	}
	objects.names.geometry.dispose()
	objects.names.material.dispose()
	const newNameMesh = setNames(newName, scene)
	objects.names = newNameMesh
}
