<template>
  <q-page class="flex flex-center">
    <MjpegVideo url="/mjpeg/main" :width="960" :height="540" />
  </q-page>
</template>

<script>
import MjpegVideo from "components/MjpegVideo.vue"

export default {
  name: "PageIndex",
  components: {
    MjpegVideo,
  },
}
</script>
