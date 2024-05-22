<script setup>
import gauge from './components/gauge.vue'
</script>


<template>
  
  <div>
    <h1>Aktuelle durchschnittliche Verspätung am Neumarkt</h1>

    <gauge :max_value="10"/>
  </div>

  <main>
    <h2> Hier soll eine Tabelle sein...</h2>
  </main>

</template>


<style scoped>

</style>
