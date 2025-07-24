<template>
  <div class="unauthorized-container">
    <h1>403 - Unauthorized</h1>
    <p>You do not have permission to access this page.</p>
    <router-link to="/">Go to Home</router-link>
  </div>
</template>

<script>
export default {
  name: 'UnauthorizedPage',
};
</script>

<style scoped>
.unauthorized-container {
  text-align: center;
  padding: 60px;
}
h1 {
  font-size: 2.5rem;
  color: #ff4d4d;
}
p {
  margin: 1rem 0;
}
</style>
