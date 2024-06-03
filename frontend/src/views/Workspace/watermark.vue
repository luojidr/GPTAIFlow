<template>
    <div class="watermark-container" :style="watermarkStyle"></div>
  </template>
  
  <script setup>
  import { ref, watch, onMounted } from 'vue'
  
  const props = defineProps({
    text: {
      type: String,
      required: true,
      default: 'Default Watermark'
    }
  })
  
  const watermarkStyle = ref({})
  
  const createWatermark = (text) => {
    const canvas = document.createElement('canvas')
    canvas.width = 400
    canvas.height = 300
    const ctx = canvas.getContext('2d')
    
    ctx.fillStyle = 'rgba(184, 184, 184, 0.5)'
    ctx.font = '32px Arial'
    ctx.rotate(-20 * Math.PI / 180)
    ctx.fillText(text, 40, 200)
    
    return `url(${canvas.toDataURL()})`
  }
  
  onMounted(() => {
    watermarkStyle.value = {
      backgroundImage: createWatermark(props.text),
      backgroundRepeat: 'repeat',
      backgroundPosition: '0 0', 
      width: '100%',
      height: '100%',
      position: 'absolute',
      top: '0',
      left: '0',
      pointerEvents: 'none'
    }
  })
  
  watch(() => props.text, (newText) => {
    watermarkStyle.value.backgroundImage = createWatermark(newText)
  })
  </script>
  
  <style scoped>
  .watermark-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
  </style>
  