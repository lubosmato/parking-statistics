<template>
  <q-page padding>
    <canvas ref="canvas" :width="width" :height="height"></canvas>

    <div style="max-width: 400px">
      <q-badge color="secondary"> Tension: {{ tension }} </q-badge>
      <q-slider v-model="tension" :min="0.0" :max="1.0" :step="0.025" />
    </div>
  </q-page>
</template>

<script>
import { fabric } from "fabric"

class CatmullRomCurveSegment {
  constructor(a, b, c, d) {
    this.a = a
    this.b = b
    this.c = c
    this.d = d
  }

  compute(t) {
    const t3 = t * t * t
    const t2 = t * t
    return {
      x: this.a.x * t3 + this.b.x * t2 + this.c.x * t + this.d.x,
      y: this.a.y * t3 + this.b.y * t2 + this.c.y * t + this.d.y,
    }
  }

  static fromPoints(p1, p2, p3, p4, tension = 0.0) {
    const a = {
      x: p1.x * -tension + p2.x * (2 - tension) + p3.x * (tension - 2) + p4.x * tension,
      y: p1.y * -tension + p2.y * (2 - tension) + p3.y * (tension - 2) + p4.y * tension,
    }
    const b = {
      x: 2 * p1.x * tension + p2.x * (tension - 3) + p3.x * (3 - 2 * tension) - p4.x * tension,
      y: 2 * p1.y * tension + p2.y * (tension - 3) + p3.y * (3 - 2 * tension) - p4.y * tension,
    }
    const c = {
      x: p3.x * tension - p1.x * tension,
      y: p3.y * tension - p1.y * tension,
    }
    const d = {
      x: p2.x,
      y: p2.y,
    }
    return new CatmullRomCurveSegment(a, b, c, d)
  }
}

class CatmulRomCurve {
  constructor() {
    this.segments = []
  }

  compute(t) {
    const globalT = t * this.segments.length
    const index = Math.floor(globalT)
    const localT = globalT - index
    return this.segments[index].compute(localT)
  }

  static fromPoints(points, tension = 0.0) {
    if (points.length < 4) {
      throw new Error("Minimum number of points is 4")
    }
    const curve = new CatmulRomCurve()
    for (let i = 0; i < points.length - 3; i++) {
      const segmentPoints = points.slice(i, i + 4)
      const segment = CatmullRomCurveSegment.fromPoints(...segmentPoints, tension)
      curve.segments.push(segment)
    }
    return curve
  }
}

export default {
  name: "PageCurvePlayground",
  data: function() {
    return {
      width: 600,
      height: 600,
      curve: null,
      curvePolyline: {},
      canvas: {},
      pointsPolyline: {},
      tension: 0.0,
    }
  },
  watch: {
    tension() {
      if (this.pointsPolyline.points.length === 0) return
      const point = this.pointsPolyline.points.pop()
      this.addPoint(point)
    },
  },
  methods: {
    onDoubleClick(event) {
      const x = event.pointer.x
      const y = event.pointer.y
      this.addPoint({ x, y })
    },
    addPoint(point) {
      this.pointsPolyline.points.push(point)

      if (this.pointsPolyline.points.length >= 2) {
        const first = this.pointsPolyline.points[0]
        const second = this.pointsPolyline.points[1]
        const preLast = this.pointsPolyline.points[this.pointsPolyline.points.length - 2]
        const last = this.pointsPolyline.points[this.pointsPolyline.points.length - 1]

        let delta = { x: first.x - second.x, y: first.y - second.y }
        let magnitude = Math.sqrt(delta.x * delta.x + delta.y * delta.y)
        const firstDirection = { x: delta.x / magnitude, y: delta.y / magnitude }

        delta = { x: last.x - preLast.x, y: last.y - preLast.y }
        magnitude = Math.sqrt(delta.x * delta.x + delta.y * delta.y)
        const lastDirection = { x: delta.x / magnitude, y: delta.y / magnitude }

        this.curve = CatmulRomCurve.fromPoints(
          [
            { x: first.x + firstDirection.x * 10, y: first.y + firstDirection.y },
            ...this.pointsPolyline.points,
            { x: last.x + lastDirection.x * 10, y: last.y + lastDirection.y },
          ],
          this.tension
        )

        this.canvas.remove(this.curvePolyline)
        this.curvePolyline = new fabric.Polyline([], {
          left: 0,
          top: 0,
          fill: "transparent",
          stroke: "black",
          strokeWidth: 2,
          selectable: false,
          objectCaching: false,
        })

        for (let t = 0.0; t <= 1.0; t += 0.001) {
          const point = this.curve.compute(t)
          this.curvePolyline.points.push(point)
        }
        this.canvas.add(this.curvePolyline)
      }
      this.canvas.renderAll()
    },
  },
  mounted() {
    this.canvas = new fabric.Canvas(this.$refs.canvas, {
      selection: false,
    })
    this.canvas.on("mouse:dblclick", this.onDoubleClick)

    this.pointsPolyline = new fabric.Polyline([], {
      left: 0,
      top: 0,
      fill: "transparent",
      stroke: "#f0f0f0",
      strokeWidth: 3,
      selectable: false,
      objectCaching: false,
    })
    this.canvas.add(this.pointsPolyline)
  },
}
</script>

<style lang="scss" scope>
canvas {
  border: 1px solid rgb(117, 117, 117);
}
</style>
