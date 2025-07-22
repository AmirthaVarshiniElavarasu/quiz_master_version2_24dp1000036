<template>
  <div class="navbar-container">
    <nav class="navbar_comp" :class="role">
      <div class="home">
        <router-link v-if="role === 'admin'" to="/admin_dashboard">Home</router-link>
        <router-link v-if="role === 'user'" to="/user_dashboard">Home</router-link>
      </div>

      <div class="quiz" v-if="role === 'admin'">
        <router-link to="/quizzes">Quiz</router-link>
      </div>

      <div class="summary" v-if="role === 'admin'">
        <router-link to="/summary">Summary</router-link>
      </div>

      <div class="logout">
        <a href="#" @click.prevent="logout">Logout</a>
      </div>

      <div id="search" class="search_class" :data-source="role">
        <input type="search" v-model="searchQuery" @input="search" placeholder="Search here"/>
      </div>

      <div id="welcome">{{ username }}</div>
    </nav>

    <div class="search-results" v-if="results.length > 0">
      <div v-html="formattedResults"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'NavBar',
  data() {
    return {
      role: '',
      username: '',
      searchQuery: '',
      results: [],
    };
  },
  computed: {
    formattedResults() {
      const grouped = this.groupResults(this.results);
      let html = '';
      for (const [category, items] of Object.entries(grouped)) {
        html += `<h3>${category}</h3>`;
        items.forEach((item) => {
          html += `<p>${Object.entries(item).map(([k, v]) => `${k}: ${v}`).join(' - ')}</p>`;
        });
      }
      return html;
    },
  },
  mounted() {
    this.role = localStorage.getItem('role') || 'user';
    this.username = localStorage.getItem('username') || 'Guest';
  },
  methods: {
   async logout() {
      const token = localStorage.getItem('token');

      try {
        const res = await fetch('http://localhost:5000/api/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token,
          },
        });

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.error || `Logout failed: ${res.status}`);
        }

        const data = await res.json();
        console.log(data.message); // Optional: success message
      } catch (error) {
        console.error('Logout error:', error.message); // Optional: show error message
      } finally {
        // Always clear localStorage and navigate away
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        this.$router.push('/');
      }
},
    async search() {
      if (this.searchQuery.trim() === '') {
        this.results = [];
        return;
      }

      const source = this.role === 'admin' ? 'admin-navbar' : 'user-navbar';
      const token = localStorage.getItem('token'); // adjust if you store token elsewhere

      try {
        const response = await axios.get('http://localhost:5000/api/search', {
          params: {
            q: this.searchQuery,
            source: source,
          },
          headers: {
            'Authentication-Token': token,
          },
        });

        const data = response.data;
        this.results = [];

        for (const key in data) {
          if (Array.isArray(data[key])) {
            this.results.push(...data[key].map((item) => ({ category: key, ...item })));
          }
        }

      } catch (err) {
        console.error('Search error', err);
        this.results = [{ category: 'Error', message: err.response?.data?.error || err.message }];
      }
    }
  ,
    groupResults(data) {
      return data.reduce((acc, curr) => {
        const category = curr.category || 'Misc';
        const item = { ...curr };
        delete item.category;
        if (!acc[category]) acc[category] = [];
        acc[category].push(item);
        return acc;
      }, {});
    },
  },
}
</script>

<style scoped>
.navbar_comp {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  background-color: #27667B;
  padding: 10px 20px;
  color: white;
}

.navbar_comp > div {
  margin: 0 10px;
}

.navbar_comp a {
  color: white;
  text-decoration: none;
  font-size: 20px;
  font-weight: bold;
  padding: 8px 12px;
  transition: 0.3s;
}

.navbar_comp a:hover {
  background-color: #143D60;
  border-radius: 5px;
}

.navbar_comp input {
  padding: 5px 10px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
}

.logout a {
  background-color: #e74c3c;
  padding: 6px 12px;
  border-radius: 5px;
}

.logout a:hover {
  background-color: #c0392b;
}

.search-results {
  color: white;
  background-color: #27667B;
  transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out;
  border-radius: 0 0 15px 15px;
  padding: 10px;
}

.search-results h3 {
  color: white !important;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .navbar_comp {
    flex-direction: column;
    align-items: center;
  }
  .navbar_comp > div {
    margin: 5px 0;
  }
  .search_class input {
    width: 100%;
  }
}
</style>
