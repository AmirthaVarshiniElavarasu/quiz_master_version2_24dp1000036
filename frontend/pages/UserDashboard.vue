<template>
  <NavBar />
  <div id="userdashboard">
    <div v-if="messages.length">
      <p v-for="(msg, index) in messages" :key="index" :class="['flash-message', msg.category]">
        {{ msg.text }}
      </p>
    </div>

    <h1 style="text-align:center">Upcoming Quizzes</h1>
    <table id="user-table-db">
      <thead>
        <tr>
          <th>Quiz ID</th>
          <th>Quiz Title</th>
          <th>No. of Questions</th>
          <th>Date</th>
          <th>Duration</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in quizzes" :key="q.quiz_id">
          <td>{{ q.quiz_id }}</td>
          <td>{{ q.quiz_title }}</td>
          <td>{{ q.total_questions }}</td>
          <td>{{ formatDate(q.quiz_date) }}</td>
          <td>{{ q.quiz_time }} Minutes</td>
          <td style="display: flex; gap: 10px;">
            <button @click="viewDetails(q)">View</button>
            <router-link :to="`/user/startquiz/${q.quiz_id}`">
              <button id="startquiz">Start</button>
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <QuizDetails v-if="showDetails" :quiz="selectedQuiz" :subject="selectedSubject" :chapter="selectedChapter" @close="showDetails = false"/>
</template>

<script>
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';
import QuizDetails from '@/components/QuizDetails.vue';

export default {
  name: 'UserDashboard',
  data() {
    return {
      quizzes: [],
      messages: [],
      chapters: [],
      selectedQuiz: null,
      selectedSubject: null,
      selectedChapter: null,
      showDetails: false,
    };
  },components:{
    NavBar,
    QuizDetails
  },
  methods: {
    async fetchQuizzes() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/user_dashboard', {
          headers: {
            'Authentication-Token': token,
          },
        });
        this.quizzes = res.data.quizzes || [];
        this.messages = res.data.messages || [];
        this.chapters = res.data.chapters || []; // Assuming backend sends flash messages like { category, text }
      } catch (err) {
        console.error('Failed to fetch quizzes', err);
      }
    },
    findSubjectId(chap_id) {
    const chapter = this.chapters.find(chap => chap.chap_id === chap_id);
    return chapter ? chapter.sub_id : null;
    },
    async viewDetails(quiz) {
      const token = localStorage.getItem('token');
      const sub_id = this.findSubjectId(quiz.chap_id);

      try {
        const res = await axios.get(`/api/quizview/${sub_id}/${quiz.chap_id}`, {
          headers: { 'Authentication-Token': token }
        });

        this.selectedQuiz = quiz;
        this.selectedSubject = res.data.subject;
        this.selectedChapter = res.data.chapter;
        this.showDetails = true;
      } catch (error) {
        console.error('Failed to load quiz details', error);
      }
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-GB'); // dd-mm-yyyy format
    },
  },
  created() {
    this.fetchQuizzes();
  },
};
</script>

<style scoped>
#user-table-db {
  width: 100%;
  border-collapse: collapse;
  margin: 20px auto;
}

#user-table-db th,
#user-table-db td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

#user-table-db th {
  background-color: #f2f2f2;
}

#viewquiz,
#startquiz {
  padding: 6px 12px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}

#startquiz {
  background-color: #28a745;
}

.flash-message {
  padding: 10px;
  margin: 10px auto;
  width: 50%;
  text-align: center;
  border-radius: 4px;
}

.flash-message.success {
  background-color: #d4edda;
  color: #155724;
}

.flash-message.error {
  background-color: #f8d7da;
  color: #721c24;
}
</style>
