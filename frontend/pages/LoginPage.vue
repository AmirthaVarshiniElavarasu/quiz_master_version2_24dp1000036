<template>
  <div class="login-page">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <div>
      <button type="submit">Login</button> 
      <router-link to="/register"><button>Register </button></router-link>
      </div>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      message: '',
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          // Save token and role
          localStorage.setItem('token', data.auth_token);
          const userRole = data.user.roles[0];
          localStorage.setItem('role', userRole);
          localStorage.setItem('username',data.user.username)
          localStorage.setItem('user_id',data.user.user_id)

          // Redirect based on role
          if (userRole === 'admin') {
            this.$router.push('/admin_dashboard');
          } else if (userRole === 'user') {
            this.$router.push('/user_dashboard');
          } else {
            this.message = 'Unknown user role.';
          }
        } else {
          this.message = data.message || 'Login failed';
        }
      } catch (error) {
        this.message = 'Server error. Please try again later.';
        console.error(error);
      }
    },
  },
};
</script>


