<template>
  <q-page padding>
    <div class="row">
      <MainVideo />
    </div>
    <div class="row">
      <RoiVideo url="/mjpeg/roi" :width="512" :height="256" />
    </div>
  </q-page>
</template>

<script>
import MainVideo from "components/MainVideo.vue"
import RoiVideo from "components/RoiVideo.vue"

export default {
  name: "PageIndex",
  components: {
    MainVideo,
    RoiVideo,
  },
}
</script>
