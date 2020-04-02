<template>
  <div>
    <p>
      Curves defines interesting areas for free parking place analysis. The main idea is not to use standard image
      pyramid but rather focus only on areas that are relevant.
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
        :rules="[val => !!val || 'Name is required', val => val.length > 2 || 'Name must have at least 3 characters']"
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
  </div>
</template>

<script>
import { fabric } from "fabric"

export default {
  name: "Curves",
  props: {
    canvas: { type: Object, required: true },
  },
  data: function() {
    return {
      selectedCurve: null,
      newCurve: {
        name: "",
        color: "#000000",
      },
      curves: [],
    }
  },
  methods: {
    addCurve() {
      const newCurve = {
        ...this.newCurve,
        index: 0,
        points: [this.addPoint(0, 0, this.newCurve.color, "0"), this.addPoint(100, 100, this.newCurve.color, "1")],
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
  },
}
</script>

<style></style>
