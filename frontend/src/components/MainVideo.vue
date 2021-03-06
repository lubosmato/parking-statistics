<template>
  <div class="full-width">
    <div class="row q-col-gutter-md">
      <div class="col-auto">
        <div :style="style">
          <img ref="image" :src="url" alt="MJPEG stream" />
          <canvas ref="canvas" :width="width" :height="height"></canvas>
        </div>
        <p>X: {{ x }} Y: {{ y }}</p>
      </div>

      <div class="col">
        <q-card>
          <q-tabs
            v-model="selectedTab"
            dense
            class="text-grey"
            active-color="primary"
            indicator-color="primary"
            align="justify"
            narrow-indicator
          >
            <q-tab name="curves" label="Curves" />
            <q-tab name="poi" label="POI" />
            <q-tab name="other" label="Other" />
          </q-tabs>
          <q-separator />

          <q-tab-panels :keep-alive="true" v-model="selectedTab" animated>
            <q-tab-panel name="curves">
              <Curves v-model="curves" @selectCurve="selectedCurve = $event" />
            </q-tab-panel>

            <q-tab-panel name="poi">
              <div class="text-h6">POI</div>
              Lorem ipsum dolor sit amet consectetur adipisicing elit.
            </q-tab-panel>

            <q-tab-panel name="other">
              <div class="text-h6">Other</div>
              Lorem ipsum dolor sit amet consectetur adipisicing elit.
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash"
import axios from "axios"
import { fabric } from "fabric"
import Curves from "components/Curves.vue"
import { createPoint } from "components/canvas.js"

const selectedRadius = 9
const notSelectedRadius = 6

export default {
  name: "MjpegVideo",
  components: { Curves },
  data() {
    return {
      width: 960,
      height: 540,
      videoFrameRate: 10,
      url: "/mjpeg/main",
      x: 0,
      y: 0,
      canvas: {},
      curves: [],
      selectedCurve: null,
      selectedTab: "curves",
      poi: {
        points: [
          { x: 0, y: 0 },
          { x: 0, y: 0 },
          { x: 0, y: 0 },
          { x: 0, y: 0 },
        ],
      },
    }
  },
  computed: {
    style() {
      return { width: `${this.width}px`, height: `${this.height}px` }
    },
  },
  watch: {
    "poi.points": _.throttle(function() {
      axios.post("/api/v1/poi", this.poi)
    }, 100),
    selectedCurve(newCurve, oldCurve) {
      if (oldCurve) {
        for (let point of oldCurve.points) {
          // TODO space for refactoring - encapsulate item(0) accessing
          point.item(0).setRadius(notSelectedRadius)
        }
      }
      if (newCurve) {
        for (let point of newCurve.points) {
          // TODO space for refactoring - encapsulate item(0) accessing
          point.item(0).setRadius(selectedRadius)
        }
      }
    },
    curves(newValue, oldValue) {
      const addedCurves = _.difference(newValue, oldValue)
      const removedCurves = _.difference(oldValue, newValue)

      for (const curve of removedCurves) {
        for (const point of curve.points) {
          this.canvas.remove(point)
        }
      }
      for (const curve of addedCurves) {
        for (const point of curve.points) {
          this.canvas.add(point)
        }
      }
    },
  },
  methods: {
    onMouseMove(event) {
      this.x = event.pointer.x
      this.y = event.pointer.y
    },
    onDoubleClick(event) {
      if (!this.selectedCurve) return

      const color = this.selectedCurve.color
      const label = this.selectedCurve.points.length.toString()
      const point = createPoint(event.pointer.x, event.pointer.y, color, label)
      // TODO space for refactoring - encapsulate item(0) accessing
      point.item(0).setRadius(selectedRadius)
      this.selectedCurve.points.push(point)
      this.canvas.add(point)

      // const position = { x: event.pointer.x, y: event.pointer.y }
      // this.$set(this.poi.points, 2, position)
    },
  },
  beforeMount() {
    axios
      .get("/api/v1/poi")
      .then(response => response.data.points)
      .then(points => {
        this.poi.points = points
      })
  },
  mounted() {
    this.canvas = new fabric.Canvas(this.$refs.canvas, {
      selection: false,
    })
    this.canvas.on("mouse:move", this.onMouseMove)
    this.canvas.on("mouse:dblclick", this.onDoubleClick)

    this.$refs.image.onload = () => {
      const video = new fabric.Image(this.$refs.image, {
        left: 0,
        top: 0,
        selectable: false,
        hoverCursor: "crosshair",
        hasControls: false,
      })
      this.canvas.add(video)

      setInterval(() => this.canvas.requestRenderAll(), 1 / this.videoFrameRate)
    }
  },
  beforeDestroy() {
    this.canvas.dispose()
  },
}
</script>

<style lang="scss" scoped>
img {
  display: none;
}
</style>
