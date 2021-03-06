<template>
  <div>
    <p>
      Curves defines interesting areas for free parking place analysis. The main idea is not to use standard image
      pyramid but rather focus only on areas that are relevant.
    </p>
    <q-list bordered class="rounded-borders">
      <q-item-label header>Available curves</q-item-label>

      <div v-for="(curve, index) in value" :key="index">
        <q-item>
          <q-item-section avatar center>
            <q-radio v-model="selectedCurve" :val="curve" />
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
                @click="deleteCurve(curve)"
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
        ref="newCurveName"
        v-model="newCurve.name"
        label="New curve name"
        placeholder="My curve"
        outlined
        :rules="[val => !!val || 'Name is required', val => val.length > 2 || 'Name must have at least 3 characters']"
      />

      <q-input v-model="newCurve.color" label="Color" outlined>
        <template v-slot:append>
          <q-icon
            name="casino"
            class="cursor-pointer"
            :style="{ color: newCurve.color }"
            @click="newCurve.color = createRandomColor()"
          />
          <q-icon name="colorize" class="cursor-pointer" :style="{ color: newCurve.color }">
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
import chroma from "chroma-js"
import { createPoint } from "components/canvas.js"

export default {
  name: "Curves",
  props: {
    value: { type: Array, required: true },
  },
  data: function() {
    return {
      selectedCurve: null,
      newCurve: {
        name: "",
        color: "#000000",
      },
    }
  },
  methods: {
    addCurve() {
      const newCurve = {
        ...this.newCurve,
        points: [createPoint(100, 100, this.newCurve.color, "0"), createPoint(200, 100, this.newCurve.color, "1")],
      }
      this.$emit("input", [...this.value, newCurve])
      this.selectedCurve = newCurve
      this.newCurve.name = ""
      this.$nextTick(() => this.$refs.newCurveName.resetValidation())
    },
    deleteCurve(curve) {
      this.selectedCurve = null
      this.$emit(
        "input",
        this.value.filter(c => c !== curve)
      )
    },
    createRandomColor() {
      return chroma.random()
    },
  },
  watch: {
    selectedCurve() {
      this.$emit("selectCurve", this.selectedCurve)
    },
  },
}
</script>

<style></style>
