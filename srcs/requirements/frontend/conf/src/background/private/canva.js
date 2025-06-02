import * as THREE from 'three';
import { setFloor, setFog, setLight, setPaddle, setBall } from './shapes';

const setAll = (scene) => {

	const floor = setFloor(scene)
	const fog = setFog(scene)
	const light = setLight(scene)
	const paddle1 = setPaddle("left")
	const paddle2 = setPaddle("right")
	const ball = setBall()
	
	return {floor, fog, light, paddle1, paddle2, ball}
}

const createCanva = (canva, elem, color) => {

	const scene = new THREE.Scene()

	const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1)
	camera.position.set(25, 5, 0)
	camera.lookAt(0, 0, 0)
	
	const renderer = new THREE.WebGLRenderer({ canvas: canva, antialias: true })
	renderer.shadowMap.enabled = true
	renderer.shadowMap.type = THREE.PCFSoftShadowMap
	renderer.toneMapping = THREE.ACESFilmicToneMapping
	renderer.toneMappingExposure = 1.2
	renderer.setSize(window.innerWidth, window.innerHeight)

	const objects = setAll(scene)

	let mesh

	switch (elem) {
		case 0:
			mesh = objects.paddle1
			scene.add(mesh)
			break
		case 1:
			mesh = objects.paddle2
			scene.add(mesh)
			break
		case 2:
			mesh = objects.ball
			scene.add(mesh)
			break
		default:
			break
	}

	switch (color) {
		case 0:
			mesh.material.color.set(0xFFFFFF)
			break
		case 1:
			mesh.material.color.set(0x2a484a)
			break
		case 2:
			mesh.material.color.set(0x2929ce)
			break
		case 3:
			mesh.material.color.set(0xb52c2c)
			break
		case 4:
			mesh.material.color.set(0xc6c62a)
			break
		case 5:
			mesh.material.color.set(0x259d31)
			break
		case 6:
			mesh.material.color.set(0xcf8f2a)
			break
		case 7:
			mesh.material.color.set(0x9e2acf)
			break
		default:
			break
	}

	let gravity = -0.001
	let bounceVelocity = 0.1
	let velocity = bounceVelocity
	let floorY = -1

	let animationFrameId

	const animate = () => {
		if (mesh) {
			velocity += gravity
    		mesh.position.y += velocity
    		if (mesh.position.y <= floorY) {
    	    	mesh.position.y = floorY
    	    	velocity = bounceVelocity
    		}
		}

    	renderer.render(scene, camera)
    	animationFrameId = requestAnimationFrame(animate)
	}

	animationFrameId = requestAnimationFrame(animate)

	const dispose = () => {
		cancelAnimationFrame(animationFrameId);
		if (objects.floor.current) {
			objects.floor.current.geometry.dispose()
			objects.floor.current.material.dispose()
			scene.remove(objects.floor.current)
		}
		if (objects.fog.current) {
			objects.fog.current.geometry.dispose()
			objects.fog.current.material.dispose()
			scene.remove(objects.fog.current)
		}
		if (objects.light.current) {
			scene.remove(objects.light.ambientLight)
			objects.light.ambientLight.dispose()
			objects.light.current.material.dispose()
			scene.remove(objects.light.current)
			objects.light.cornerLights.forEach(light => {
				scene.remove(objects.light)
				objects.light.dispose()
			})
		}
		if (objects.paddle1.current) {
			objects.paddle1.current.geometry.dispose()
			objects.paddle1.current.material.dispose()
			if (elem === 0) scene.remove(objects.paddle1.current)
		}
		if (objects.paddle2.current) {
			objects.paddle2.current.geometry.dispose()
			objects.paddle2.current.material.dispose()
			if (elem === 1) scene.remove(objects.paddle2.current)
		}
		if (objects.ball.current) {
			objects.ball.current.geometry.dispose()
			objects.ball.current.material.dispose()
			if (elem === 2) scene.remove(objects.ball.current)
		}
		renderer.dispose()
	}

	return {dispose, renderer, camera}
};

export default createCanva