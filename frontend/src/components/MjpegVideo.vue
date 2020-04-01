<template>
  <div>
    <img ref="image" :src="url" alt="MJPEG stream" />
    <canvas
      @click="onClick"
      @mousemove="onMouseMove"
      @touchmove="onTouchMove"
      ref="canvas"
      :width="width"
      :height="height"
    ></canvas>
  </div>
</template>

<script>
function clamp(value, min, max) {
  if (value > max) return max
  if (value < min) return min
  return value
}

export default {
  name: "MjpegVideo",
  props: {
    width: { type: Number, required: true },
    height: { type: Number, required: true },
    value: {
      type: Object,
      default: () => {
        return { x: 0, y: 0 }
      },
    },
    frameRate: { type: Number, default: 60 },
    url: { type: String, required: true },
  },
  data() {
    return {
      x: 0,
      y: 0,
      context: null,
    }
  },
  methods: {
    onTouchMove(event) {
      const rect = this.$refs.canvas.getBoundingClientRect()
      const clientX = event.touches[0]?.clientX
      const clientY = event.touches[0]?.clientY
      this.x = clamp(Math.round(clientX - rect.left), 0, rect.width - 1)
      this.y = clamp(Math.round(clientY - rect.top), 0, rect.height - 1)

      this.$emit("input", { x: this.x, y: this.y })
    },
    onMouseMove(event) {
      const rect = this.$refs.canvas.getBoundingClientRect()
      this.x = clamp(Math.round(event.clientX - rect.left), 0, rect.width - 1)
      this.y = clamp(Math.round(event.clientY - rect.top), 0, rect.height - 1)

      this.$emit("input", { x: this.x, y: this.y })
    },
    onClick(event) {
      const rect = this.$refs.canvas.getBoundingClientRect()
      const x = clamp(Math.round(event.clientX - rect.left), 0, rect.width - 1)
      const y = clamp(Math.round(event.clientY - rect.top), 0, rect.height - 1)

      this.$emit("click", { x, y })
    },
    draw() {
      const context = this.context
      context.clearRect(0, 0, this.width, this.height)

      context.drawImage(this.$refs.image, 0, 0)

      // context.beginPath()
      // context.moveTo(0, 0)
      // context.lineTo(this.x, this.y)
      // context.stroke()
    },
  },
  mounted() {
    this.context = this.$refs.canvas.getContext("2d")
    setInterval(this.draw, 1000 / this.frameRate)
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
