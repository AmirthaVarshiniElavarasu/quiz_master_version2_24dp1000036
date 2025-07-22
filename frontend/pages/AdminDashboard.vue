<template>
  <NavBar />
  <div class="dashboard">
    <h2 class="text-center">Welcome, {{ username }}</h2>
    <div v-if="subjects.length === 0" class="no-data">No subjects found.</div>

    <div v-for="subject in subjects" :key="subject.sub_id" class="subject-card">
      <h3>{{ subject.sub_name }}</h3>

      <button @click="toggleDescription(subject.sub_id)">
        {{ visibleDescriptions.includes(subject.sub_id) ? 'Hide' : 'Show' }} Details
      </button>

      <div v-show="visibleDescriptions.includes(subject.sub_id)">
        <p><strong>Subject Description:</strong> {{ subject.sub_Description }}</p>
      </div>

      <table class="chapter-table">
        <thead>
          <tr>
            <th>Chapter Title</th>
            <th>No. of Quizzes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="chapter in chaptersBySubject(subject.sub_id)"
            :key="chapter.chap_id"
          >
            <td>{{ chapter.chap_title }}</td>
            <td>{{ getQuizCount(chapter.chap_id) }}</td>
            <td>
              <button @click="editChapter(chapter)">Edit</button>
              <button @click="deleteChapter(chapter)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <button @click="addChapter(subject.sub_id)">Add Chapter</button>
      <hr />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      username: '',
      subjects: [],
      chapters: [],
      visibleDescriptions: [],
      quizzes: [],
    };
  },
  components: {
    NavBar,
  },
  methods: {
    async fetchData() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/admin_dashboard', {
          headers: {
            'Authentication-Token': token,
          },
        });
        this.subjects = res.data.subjects || [];
        this.chapters = res.data.chapters || [];
        this.quizzes = res.data.quizzes || [];
        this.username = res.data.user || 'Admin';
      } catch (err) {
        console.error('Failed to load admin data', err);
        this.$router.push('/login'); // Redirect if token is invalid
      }
    },
    chaptersBySubject(sub_id) {
      return this.chapters.filter((c) => c.sub_id === sub_id);
    },
    getQuizCount(chap_id) {
      return this.quizzes.filter((q) => q.chap_id === chap_id).length;
    },
    toggleDescription(subId) {
      const idx = this.visibleDescriptions.indexOf(subId);
      if (idx > -1) {
        this.visibleDescriptions.splice(idx, 1);
      } else {
        this.visibleDescriptions.push(subId);
      }
    },
    editChapter(chapter) {
      this.$router.push({ name: 'EditChapter', params: { chap_id: chapter.chap_id } });
    },
    deleteChapter(chapter) {
      if (confirm(`Are you sure you want to delete "${chapter.chap_title} ${chapter.chap_id}"?`)) {
        const token = localStorage.getItem('token');
        axios.delete(`/api/chapters/${chapter.chap_id}`, {
            headers: {
              'Authentication-Token': token,
            },
          })
          .then(() => {
            this.chapters = this.chapters.filter(c => c.chap_id !== chapter.chap_id);
          })
          .catch((err) => {
            console.error('Failed to delete chapter:', err);
              if (err.response && err.response.data && err.response.data.message) {
                   alert(`Error: ${err.response.data.message}`);} 
              else {
                    alert('Error deleting chapter.');
                  }
          });
      }
    },
    addChapter(subId) {
      this.$router.push({ name: 'CreateChapter', params: { sub_id: subId } });
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style scoped>
.dashboard {
  padding: 2rem;
}
.text-center {
  text-align: center;
}
.subject-card {
  border: 1px solid #ccc;
  padding: 1rem;
  margin-bottom: 2rem;
  border-radius: 10px;
}
.chapter-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.chapter-table th,
.chapter-table td {
  border: 1px solid #aaa;
  padding: 0.5rem;
  text-align: left;
}
button {
  margin-right: 0.5rem;
  margin-top: 0.5rem;
}
.no-data {
  color: red;
  font-weight: bold;
}
</style>
