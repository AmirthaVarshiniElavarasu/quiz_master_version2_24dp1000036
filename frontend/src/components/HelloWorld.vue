<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: ''
    }
  },
  mounted() {
    fetch('http://localhost:5000/api/hello')
      .then(res => res.json())
      .then(data => {
        this.message = data.message;
      })
  }
}
</script>
