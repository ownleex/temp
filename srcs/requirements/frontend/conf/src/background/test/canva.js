import * as THREE from 'three';
import { setFloor, setFog, setLine, setPilar, setBorder, setBScreen, setLight, setPaddle, setWall, setBall } from './shapes';

const setAll = (scene) => {

	const floor = setFloor(scene)
	const fog = setFog(scene)
	const line = setLine(scene)
	const pilar = setPilar(scene)
	const border = setBorder(scene)
	const bscreen = setBScreen(scene)
	const light = setLight(scene)
	const paddle1 = setPaddle(scene, "left")
	const paddle2 = setPaddle(scene, "right")
	const wall1 = setWall(scene, "left")
	const wall2 = setWall(scene, "right")
	const ball = setBall(scene)
	
	return {floor, fog, line, pilar, border, bscreen, light, paddle1, paddle2, wall1, wall2, ball}
}

const createCanva = (canva) => {
	
	const scene = new THREE.Scene()

	const camera = new THREE.PerspectiveCamera(60, canva.width / canva.height, 0.1)
	camera.position.set(40, 20, 0)
	camera.lookAt(0, 5, 0)
	
	const renderer = new THREE.WebGLRenderer({ canvas: canva, antialias: false })
	renderer.shadowMap.enabled = true
	renderer.shadowMap.type = THREE.VSMShadowMap
	renderer.toneMapping = THREE.ACESFilmicToneMapping
	renderer.toneMappingExposure = 1.2
	renderer.setSize(canva.width, canva.height)
	renderer.setPixelRatio(0.3)

	const objects = setAll(scene)

	const radius = 50
	let angle = 0

	let animationFrameId

	const animate = () => {
		renderer.render(scene, camera)
		angle += 0.001
		camera.position.x = radius * Math.cos(angle);
  		camera.position.z = radius * Math.sin(angle);
		camera.lookAt(0, 5, 0)
		animationFrameId = requestAnimationFrame(animate)
	}

	animationFrameId = requestAnimationFrame(animate);

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
		if (objects.line.current) {
			for (let i = 0; i < objects.line.current.n; i++) {
				objects.line.current.cubes[i].geometry.dispose()
				objects.line.current.cubes[i].material.dispose()
				scene.remove(objects.line.current.cubes[i])
			}
		}
		if (objects.pilar.current) {
			objects.pilar.current.pilarL.geometry.dispose()
			objects.pilar.current.pilarR.geometry.dispose()
			objects.pilar.current.pilarL.material.dispose()
			objects.pilar.current.pilarR.material.dispose()
			scene.remove(objects.pilar.current.pilarL)
			scene.remove(objects.pilar.current.pilarR)
		}
		if (objects.border.current) {
			objects.border.current.geometry.dispose()
			objects.border.current.material.dispose()
			scene.remove(objects.border.current)
		}
		if (objects.bscreen.current) {
			objects.bscreen.current.geometry.dispose()
			objects.bscreen.current.material.dispose()
			scene.remove(objects.bscreen.current)
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

	return {dispose, renderer, camera};
};

export default createCanva