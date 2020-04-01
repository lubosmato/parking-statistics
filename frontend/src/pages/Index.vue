<template>
  <q-page>
    <MjpegVideo url="/mjpeg/main" :width="960" :height="540" v-model="position" @click="click" />
    <p>X: {{ position.x }}, Y: {{ position.y }}</p>

    <MjpegVideo url="/mjpeg/roi" :width="512" :height="256" v-model="roiPosition" />
    {{ poi }}
  </q-page>
</template>

<script>
import axios from "axios"
import MjpegVideo from "components/MjpegVideo.vue"

export default {
  name: "PageIndex",
  components: {
    MjpegVideo,
  },
  data: function() {
    return {
      position: { x: 0, y: 0 },
      roiPosition: { x: 0, y: 0 },
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
  watch: {
    ["poi.points"]() {
      axios.post("/api/v1/poi", this.poi).then(console.log, console.error)
    },
  },
  methods: {
    click(a) {
      this.$set(this.poi.points, 2, a)
    },
  },
  async beforeRouteEnter(to, from, next) {
    axios
      .get("/api/v1/poi")
      .then(response => response.data.points)
      .then(points => {
        next(vm => (vm.poi.points = points))
      })
  },
}
</script>
