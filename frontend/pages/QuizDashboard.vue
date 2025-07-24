<template>
  <div>
    <NavBar />

    <div class="container">
      <h3>All Quizzes</h3>

      <table>
        <thead>
          <tr>
            <th>Quiz ID</th>
            <th>Quiz Title</th>
            <th>No. of Questions</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in quizzes" :key="quiz.quiz_id">
            <td>{{ quiz.quiz_id }}</td>
            <td><router-link :to="`/questions/${quiz.quiz_id}`"> {{ quiz.quiz_title }} </router-link></td>
            <td>{{ quiz.total_questions }}</td>
            <td>
              <button @click="editQuiz(quiz)">Edit</button>
              <button @click="deleteQuiz(quiz)">Delete</button>
              <button @click="viewDetails(quiz)">View</button>
            </td>
          </tr>
        </tbody>
      </table>

      <button @click="addQuiz()">Add Quiz</button>
    </div>
  </div>
  <QuizForm :visible="showQuizForm" :isEdit="isEditingQuiz" :quizData="selectedQuiz" :chapters="chapters" @close="showQuizForm = false" @submitted="handleQuizSubmit" />
  <QuizDetails v-if="showDetails" :quiz="selectedQuiz" :subject="selectedSubject" :chapter="selectedChapter" @close="showDetails = false"/>

</template>


<script>
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';
import QuizForm from '@/components/QuizForm.vue';
import QuizDetails from '@/components/QuizDetails.vue';



export default {
  name: 'QuizDashboard',
  
  data() {
    return {
      username: '',
      quizzes: [],
      chapters: [],
      // Quiz
      showQuizForm: false,
      isEditingQuiz: false,
      selectedQuiz: null,
      showDetails: false,
      selectedSubject: null,
      selectedChapter: null
    };
  },
  components: { 
    NavBar,
   QuizForm,
   QuizDetails 
},
  methods: {
    async fetchData() {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get('/api/quizzes', {
            headers: {
                'Authentication-Token': token,
            },
            });

            this.quizzes = res.data.quizzes || [];
            this.chapters = res.data.chapters || []; 
            this.username = res.data.user || '';
        } catch (err) {
            console.error('Failed to load quiz data', err);
            this.$router.push('/login');
        }
        },
    deleteQuiz(quiz) {
      if (confirm(`Are you sure you want to delete "${quiz.quiz_title}"?`)) {
        const token = localStorage.getItem('token');
        axios.delete(`/api/quizzes/${quiz.quiz_id}`, {
            headers: {
              'Authentication-Token': token,
            },
          })
          .then(() => {
            this.fetchData();
          })
          .catch((err) => {
            console.error('Failed to delete quiz:', err);
              if (err.response && err.response.data && err.response.data.message) {
                   alert(`Error: ${err.response.data.message}`);} 
              else {
                    alert('Error deleting quiz.');
                  }
          });
      }
    },

    addQuiz() {
        this.selectedQuiz = {
            quiz_title: '',
            chap_id: '',
            quiz_description: '',
            quiz_date: '',
            quiz_time: '',
            quiz_duration_hours: 0,
            quiz_duration_minute: 0,
        };
        this.isEditingQuiz = false;
        this.showQuizForm = true;
        },
    editQuiz(quiz) {
    this.selectedQuiz = {
        quiz_id: quiz.quiz_id,
        chap_id: quiz.chap_id,
        quiz_title: quiz.quiz_title,
        quiz_description: quiz.quiz_description,
        quiz_date: quiz.quiz_date,
        quiz_time: quiz.quiz_time,
    };
    this.isEditingQuiz = true;
    this.showQuizForm = true;
    },
    handleQuizSubmit() {
      this.showQuizForm = false;
      this.fetchData();
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
    }
  },
  mounted() {
    this.fetchData();
  },
};
</script>
