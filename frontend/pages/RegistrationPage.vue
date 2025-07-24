<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input v-model="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <input v-model="username" placeholder="Username" required />
      <input v-model="qualification" placeholder="Qualification" />
      <input v-model="gender" placeholder="Gender" />
      <input v-model="dob" type="date" required />
      <button type="submit">Register</button>
      <router-link to="/login">Login</router-link>
    </form>
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      username: '',
      qualification: '',
      gender: '',
      dob: '',
      message: ''
    };
  },
  methods: {
    async register() {
      const res = await fetch('http://localhost:5000/api/registration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: this.email,
          password: this.password,
          username: this.username,
          qualification: this.qualification,
          gender: this.gender,
          dob: this.dob
        })
      });

      const data = await res.json();
      if (res.ok) {
        this.message = data.message;
        this.$router.push('/login');
      } else {
        this.message = data.message;
      }
    }
  }
};
</script>
