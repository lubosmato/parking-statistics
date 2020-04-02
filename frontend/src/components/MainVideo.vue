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

          <q-tab-panels v-model="selectedTab" animated>
            <q-tab-panel name="curves">
              <p>
                Curves defines interesting areas for free parking place analysis. The main idea is not to use standard
                image pyramid but rather focus only on areas that are relevant.
              </p>
              <q-list bordered class="rounded-borders">
                <q-item-label header>Available curves</q-item-label>

                <div v-for="(curve, index) in curves" :key="index">
                  <q-item>
                    <q-item-section avatar center>
                      <q-radio :val="curve" v-model="selectedCurve" />
                    </q-item-section>

                    <q-item-section avatar center>
                      <q-icon name="mdi-vector-curve" :style="{ color: curve.color }" size="3em" />
                    </q-item-section>

                    <q-item-section center>
                      <q-item-label caption>
                        <div class="text-subtitle2">{{ curve.name }}</div>
                        <q-badge
                          :style="{ background: curve.color }"
                          class="q-ma-xs"
                          v-for="(point, pointIndex) in curve.points"
                          :key="pointIndex"
                        >
                          [{{ pointIndex }}] X: {{ point.left }}, Y: {{ point.top }}
                        </q-badge>
                      </q-item-label>
                    </q-item-section>

                    <q-item-section center side>
                      <div class="text-grey-8 q-gutter-xs">
                        <q-btn
                          class="gt-xs"
                          size="16px"
                          flat
                          dense
                          round
                          icon="delete"
                          color="red-8"
                          @click="deleteCurve(index)"
                        />
                      </div>
                    </q-item-section>
                  </q-item>
                  <q-separator spaced />
                </div>
              </q-list>

              <q-separator class="q-my-md" />
              <div class="text-h6 q-pb-sm">Add curve</div>
              <q-form @submit="addCurve" class="q-gutter-md">
                <q-input
                  v-model="newCurve.name"
                  label="New curve name"
                  placeholder="My curve"
                  outlined
                  :rules="[
                    val => !!val || 'Name is required',
                    val => val.length > 2 || 'Name must have at least 3 characters',
                  ]"
                />

                <q-input v-model="newCurve.color" outlined>
                  <template v-slot:append>
                    <q-icon name="colorize" class="cursor-pointer">
                      <q-popup-proxy transition-show="scale" transition-hide="scale">
                        <q-color v-model="newCurve.color" />
                      </q-popup-proxy>
                    </q-icon>
                  </template>
                </q-input>

                <q-btn color="primary" label="Add new curve" type="submit" />
              </q-form>
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

export default {
  name: "MjpegVideo",
  data() {
    return {
      width: 960,
      height: 540,
      videoFrameRate: 10,
      url: "/mjpeg/main",
      x: 0,
      y: 0,
      canvas: null,
      selectedTab: "curves",
      selectedCurve: null,
      newCurve: {
        name: "",
        color: "#000000",
      },
      curves: [],
      canvasPoints: [],
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
  },
  methods: {
    addCurve() {
      const newCurve = {
        ...this.newCurve,
        index: 0,
        points: [
          this.addPoint(0, 0, this.newCurve.color, "0"),
          this.addPoint(100, 100, this.newCurve.color, "1"),
          this.addPoint(100, 100, this.newCurve.color, "2"),
          this.addPoint(100, 100, this.newCurve.color, "3"),
          this.addPoint(100, 100, this.newCurve.color, "4"),
          this.addPoint(100, 100, this.newCurve.color, "3"),
          this.addPoint(100, 100, this.newCurve.color, "4"),
          this.addPoint(100, 100, this.newCurve.color, "3"),
          this.addPoint(100, 100, this.newCurve.color, "4"),
          this.addPoint(100, 100, this.newCurve.color, "3"),
          this.addPoint(100, 100, this.newCurve.color, "4"),
        ],
      }
      this.curves.push(newCurve)
      this.selectedCurve = newCurve
      this.newCurve.name = ""
    },
    addPoint(x, y, color, label) {
      const point = new fabric.Circle({
        fill: color,
        radius: 6,
        stroke: "black",
      })
      point.setShadow("2px 2px 2px rgba(0, 0, 0, 0.4)")
      const text = new fabric.Text(label, {
        fontFamily: "Roboto",
        fill: color,
        fontSize: 16,
        top: -18,
      })
      const group = new fabric.Group([point, text], {
        left: x,
        top: y,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        hasControls: false,
        hasBorders: false,
      })
      this.canvas.add(group)
      return group
    },
    deleteCurve(index) {
      for (const point of this.curves[index].points) {
        this.canvas.remove(point)
      }
      this.curves.splice(index, 1)
      if (this.curves.length === 0) this.selectedCurve = null
      else this.selectedCurve = this.curves[this.curves.length - 1]
    },
    onMouseMove(event) {
      this.x = event.pointer.x
      this.y = event.pointer.y
    },
    onDoubleClick(event) {
      const position = { x: event.pointer.x, y: event.pointer.y }
      this.$set(this.poi.points, 2, position)
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
    this.canvas = new fabric.Canvas(this.$refs.canvas)
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

      this.addPoint(100, 200, "#d9ff00", "0")
      setInterval(() => this.canvas.requestRenderAll(), 1 / this.videoFrameRate)
    }
  },
}
</script>

<style lang="scss" scoped>
img {
  display: none;
}
</style>
