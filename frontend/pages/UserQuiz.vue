<template>
    <NavBar/>
  <div id="user-start-quiz" class="quiz-wrapper">
    <h1>{{ quizzes.quiz_title }}</h1>
    <h3 id="time">{{ formattedTime }}</h3>

    <div v-if="questions.length > 0" id="quiz-container">
      <div v-for="(q, index) in questions" :key="q.ques_id" class="question-box">
        <p><strong>Question {{ index + 1 }}:</strong> {{ q.ques_statement }}</p>
        <div class="options">
          <label v-for="(opt, i) in q.options" :key="i">
            <input
              type="radio"
              :name="'question_' + q.ques_id"
              :value="opt.op_statement"
              v-model="userAnswers[q.ques_id]"
            />
            {{ opt.op_statement}}
          </label>
        </div>
      </div>

      <div class="submit-controls">
        <button @click="showPopup = true">Submit</button>
        <router-link to="/user_dashboard"><button>Cancel</button></router-link>
      </div>
    </div>

    <div v-else>
      <p>No questions available.</p>
    </div>

    <!-- Popup Confirmation -->
    <div v-if="showPopup" class="popup-overlay">
      <div class="popup-box">
        <h3>Are you sure you want to submit this quiz?</h3>
        <router-link :to="`/user/score/${user.id}`"><button @click="submitQuiz">Yes, Submit</button></router-link>
        <button @click="showPopup = false">Cancel</button>
      </div>
    </div>

    <div v-if="timeOver" class="time-over">
      <h2>Time Over! Quiz has been submitted.</h2>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';

export default {
  name: 'UserQuiz',
  data() {
    return {
      quizzes: {},
      questions: [],
      user:{},
      userAnswers: {},
      totalTime: 0,
      formattedTime: '',
      countdown: null,
      showPopup: false,
      timeOver: false,
    };
  },
  components:{
     NavBar
  },
  methods: {
    async fetchQuizData() {
      const token = localStorage.getItem('token');
      const quizId = this.$route.params.quiz_id;
      this.userAnswers = {};
      this.questions.forEach(q => {
      this.userAnswers[q.ques_id] = ''; 
    });

      try {
        const res = await axios.get(`/api/questions_page/${quizId}`, {
          headers: { 'Authentication-Token': token },
        });

        this.quizzes = res.data.quizzes;
        this.questions = res.data.questions;
        this.user= res.data.user;

        // Set timer in seconds
        this.totalTime = this.quizzes.quiz_time * 60;
        this.startTimer();
      } catch (err) {
        console.error('Error fetching quiz data:', err);
      }
    },
    startTimer() {
      this.updateFormattedTime();
      this.countdown = setInterval(() => {
        if (this.totalTime <= 0) {
          clearInterval(this.countdown);
          this.autoSubmit();
          return;
        }
        this.totalTime--;
        this.updateFormattedTime();
      }, 1000);
    },
    updateFormattedTime() {
      const minutes = Math.floor(this.totalTime / 60);
      const seconds = this.totalTime % 60;
      this.formattedTime = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    },
    async submitQuiz() {
      this.showPopup = false;
      await this.sendSubmission();
    },
    async autoSubmit() {
      this.timeOver = true;
      await this.sendSubmission();
    },
    async sendSubmission() {
      const token = localStorage.getItem('token');
      try {
        const quiz_id = this.quizzes.quiz_id;
        const res = await fetch(`/api/quiz_submission/${quiz_id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token,
          },
          body: JSON.stringify(this.userAnswers),
        });
        const data = await res.json();
        if (data.redirect_url) {
          this.$router.push(data.redirect_url);
        }
      } catch (err) {
        console.error('Error submitting quiz:', err);
      }
    },
  },
  created() {
    this.fetchQuizData();
  },
};
</script>


