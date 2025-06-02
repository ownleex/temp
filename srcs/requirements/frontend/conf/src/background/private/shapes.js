import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js'
import { AmbientLight, DirectionalLight } from 'three'

export const setFloor = (scene) => {
	const geometry = new THREE.PlaneGeometry(300, 300)
	const material = new THREE.MeshStandardMaterial({color: 0x7fdce2})
	const floor = new THREE.Mesh(geometry, material)
	floor.position.set(0, -1.5, 0)
	floor.rotateX(-Math.PI * 0.5)
	floor.receiveShadow = true
	scene.add(floor)
	return floor
}

export const setFog = (scene) => {
	const bg = new THREE.Color(0x326e72)
	const fog = new THREE.Fog(0x326e72, 15, 150)
	scene.background = bg
	scene.fog = fog
	return {bg, fog}
}

export const setLight = (scene) => {
	const ambientLight = new AmbientLight(0xffffff, 0.6)
	const dirLight = new DirectionalLight(0xffffff, 0.7)

	dirLight.position.set(-3, 20, 0)
	dirLight.castShadow = true
	dirLight.shadow.mapSize.set(1024, 1024)
	dirLight.shadow.camera.top = 35
	dirLight.shadow.camera.bottom = -35
	dirLight.shadow.camera.left = -30
	dirLight.shadow.camera.right = 30
	dirLight.shadow.radius = 10
	scene.add(ambientLight, dirLight)
	return {ambientLight, dirLight}
}

export const setPaddle = () => {
	const geometry = new RoundedBoxGeometry(5, 1, 1, 5, 0.5)
	const material = new THREE.MeshStandardMaterial({color: 0x2a484a})
	const paddle = new THREE.Mesh(geometry, material)
	paddle.castShadow = true
	paddle.receiveShadow = true
	paddle.position.set(0, 3, 0)
	paddle.rotateY(-Math.PI / 2)
	return paddle
}

export const setBall = () => {
	const geometry = new RoundedBoxGeometry(1, 1, 1, 5, 0.5)
	const material = new THREE.MeshStandardMaterial({color: 0xffaa00})
	const ball = new THREE.Mesh(geometry, material)
	ball.castShadow = true
	ball.receiveShadow = true
	ball.position.set(0, 3, 0)
    ball.velocity = new THREE.Vector3((Math.random() > 0.5 ? 1 : -1) * 0.1, 0, (Math.random() > 0.5 ? 1 : -1) * 0.1)
	return ball
}
