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
    <button @click="showsettimer=true">Set Daily Reminder Time</button>
    <div class="reminder-section" v-if="showsettimer">
    <p>set timer in 24 hours format</p>
    <label for="reminderHour">Hour:</label>
    <input type="number" id="reminderHour" v-model="reminderHour" min="0" max="23" />
    <label for="reminderMinute">Minute:</label>
    <input type="number" id="reminderMinute" v-model="reminderMinute" min="0" max="59" />
    <button @click="updateReminderTime">Save Reminder Time</button>

    <p v-if="reminderMessage" style="color: green">{{ reminderMessage }}</p>
  </div>


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
      setupTime: '',
      selectedQuiz: null,
      selectedSubject: null,
      selectedChapter: null,
      showDetails: false,
      showsettimer: false
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
        this.chapters = res.data.chapters || [];
        this.setupTime = res.data.setup_time || ''
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
      return date.toLocaleDateString('en-GB'); 
    },
    async updateReminderTime() {
    const token = localStorage.getItem('token');
    try {
      const res = await axios.put('/api/user/reminder-time', {
        hour: this.reminderHour || 19,
        minute: this.reminderMinute|| 0
      }, {
        headers: {
          'Authentication-Token': token
        }
      });
      this.reminderMessage = res.data.message;
      this.showsettimer = false
    } catch (error) {
      this.reminderMessage = "Failed to set reminder time.";
      console.error("Reminder time update failed", error);
    }
  }
  },
  created() {
    this.fetchQuizzes();
  },
};
</script>

