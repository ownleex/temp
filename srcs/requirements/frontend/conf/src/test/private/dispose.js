const dispose = (objects, scene, rendererRef, animationFrameId) => {
	cancelAnimationFrame(animationFrameId)
	if (objects.floor) {
		objects.floor.geometry.dispose()
		objects.floor.material.dispose()
		scene.remove(objects.floor)
	}
	if (objects.border) {
		objects.border.geometry.dispose()
		objects.border.material.dispose()
		scene.remove(objects.border)
	}
	if (objects.bscreen) {
		objects.bscreen.bscreen1.geometry.dispose()
		objects.bscreen.bscreen1.material.dispose()
		scene.remove(objects.bscreen.bscreen1)
		objects.bscreen.bscreen2.geometry.dispose()
		objects.bscreen.bscreen2.material.dispose()
		scene.remove(objects.bscreen.bscreen2)
		objects.bscreen.bscreen3.geometry.dispose()
		objects.bscreen.bscreen3.material.dispose()
		scene.remove(objects.bscreen.bscreen3)
	}
	if (objects.paddle) {
		objects.paddle.paddleL.geometry.dispose()
		objects.paddle.paddleL.material.dispose()
		scene.remove(objects.paddle.paddleL)
		objects.paddle.paddleR.geometry.dispose()
		objects.paddle.paddleR.material.dispose()
		scene.remove(objects.paddle.paddleR)
	}
	if (objects.wall) {
		objects.wall.wallL.geometry.dispose()
		objects.wall.wallL.material.dispose()
		scene.remove(objects.wall.wallL)
		objects.wall.wallR.geometry.dispose()
		objects.wall.wallR.material.dispose()
		scene.remove(objects.wall.wallR)
	}
	if (objects.ball) {
		objects.ball.geometry.dispose()
		objects.ball.material.dispose()
		scene.remove(objects.ball)
	}
	if (objects.score) {
		objects.score.geometry.dispose()
		objects.score.material.map.dispose()
		objects.score.material.dispose()
		scene.remove(objects.score)
	}
	if (objects.names) {
		objects.names.geometry.dispose()
		objects.names.material.map.dispose()
		objects.names.material.dispose()
		scene.remove(objects.names)
	}
	if (objects.light) {
		scene.remove(objects.light.ambientLight)
		scene.remove(objects.light.dirLight)
		if (objects.light.dirLight.target) scene.remove(objects.light.dirLight.target)
	}
	scene.fog = null
	scene.background = null
	rendererRef.current.dispose()
}

export default dispose
