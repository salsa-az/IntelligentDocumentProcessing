<template>
  <router-view />
  <AlertContainer />
</template>

<script>
import './charts/ChartjsConfig';
import AlertContainer from './components/AlertContainer.vue'

export default {
  components: {
    AlertContainer
  }
}
</script>

