<template>
  <div :style="style">
    <img ref="image" :src="url" alt="ROI MJPEG stream" />
    <canvas ref="canvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script>
import { fabric } from "fabric"

export default {
  name: "RoiVideo",
  props: {
    width: { type: Number, required: true },
    height: { type: Number, required: true },
    frameRate: { type: Number, default: 60 },
    url: { type: String, required: true },
  },
  data() {
    return {
      x: 0,
      y: 0,
      canvas: null,
    }
  },
  computed: {
    style() {
      return { width: `${this.width}px`, height: `${this.height}px` }
    },
  },
  mounted() {
    this.canvas = new fabric.Canvas(this.$refs.canvas, {
      selection: false,
      isDrawingMode: false,
      defaultCursor: "crosshair",
    })
    this.canvas.on("mouse:move", this.onMouseMove)

    this.$refs.image.onload = () => {
      const video = new fabric.Image(this.$refs.image, {
        left: 0,
        top: 0,
        selectable: false,
        hoverCursor: "crosshair",
        hasControls: false,
      })
      this.canvas.add(video)
      setInterval(() => this.canvas.requestRenderAll(), 1 / this.frameRate)
    }
  },
}
</script>

<style lang="scss" scoped>
img {
  display: none;
}
canvas {
  cursor: crosshair;
}
</style>
