<template>
  <NavBar />
  <div class="question-page">
    <h2>Questions for Quiz ID: {{ quizId }}</h2>

    <div v-if="loading">Loading questions...</div>

    <table v-else class="question-table">
      <thead>
        <tr>
          <th>Question ID</th>
          <th>Question Statement</th>
          <th>Options</th>
          <th>Correct Option</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="question in questions" :key="question.ques_id">
          <td>{{ question.ques_id }}</td>
          <td>{{ question.ques_statement }}</td>
          <td>
            <ul>
              <li v-for="opt in question.options" :key="opt.op_id">
                {{ opt.op_statement }}
              </li>
            </ul>
          </td>
          <td>{{ question.correct_option?.op_statement || 'N/A' }}</td>
          <td>
            <button @click="editQuestion(question)">Edit</button>
            <button @click="deleteQuestion(question.ques_id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="add-button">
      <button @click="addQuestion">Add Question</button>
    </div>

    <QuestionForm
      v-if="showQuestionForm"
      :visible="showQuestionForm"
      :isEdit="isEditingQuestion"
      :questionData="selectedQuestion"
      :quizId="quizId"
      @submitted="handleFormSubmit"
      @close="closeQuestionForm"
    />
  </div>
</template>

<script>
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';
import QuestionForm from '@/components/QuestionForm.vue';

export default {
  name: 'QuestionsPage',
  components: { QuestionForm, NavBar },
  data() {
    return {
      quizId: this.$route.params.quiz_id,
      questions: [],
      loading: true,
      showQuestionForm: false,
      isEditingQuestion: false,
      selectedQuestion: null
    };
  },
  methods: {
    async fetchQuestions() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get(`/api/questions_page/${this.quizId}`, {
          headers: {
            'Authentication-Token': token,
          },
        });
        this.questions = res.data.questions || [];
      } catch (err) {
        console.error('Failed to fetch questions:', err);
      } finally {
        this.loading = false;
      }
    },
    deleteQuestion(ques_id) {
      if (!confirm('Are you sure you want to delete this question?')) return;
      const token = localStorage.getItem('token');
      axios.delete(`/api/questions/${ques_id}`, {
        headers: {
          'Authentication-Token': token,
        },
      })
      .then(() => {
        this.questions = this.questions.filter(q => q.ques_id !== ques_id);
      })
      .catch(() => {
        alert('Failed to delete question.');
      });
    },
    editQuestion(question) {
      this.selectedQuestion = { ...question };
      this.isEditingQuestion = true;
      this.showQuestionForm = true;
    },
   
    addQuestion() {
      this.selectedQuestion = {
        quiz_id: this.quizId,
        ques_statement: '',
        ques_id: null,
        correct_option: null,
        options: [
          { op_statement: '' },
          { op_statement: '' }
        ]
      };
      this.isEditingQuestion = false;
      this.showQuestionForm = true;
    },

    closeQuestionForm() {
      this.showQuestionForm = false;
      this.selectedQuestion = null;
    },
    handleFormSubmit() {
      this.closeQuestionForm();
      this.fetchQuestions();
    },
    
  },
  mounted() {
    this.fetchQuestions();
  }
};
</script>

