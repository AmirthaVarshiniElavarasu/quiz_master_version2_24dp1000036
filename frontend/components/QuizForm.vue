<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-box">
      <h2>{{ isEdit ? 'Edit' : 'Add' }} Quiz</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Chapter:</label>
          <select v-model="quiz.chap_id" required>
            <option disabled value="">Select Chapter</option>
            <option v-for="chapter in chapters" :key="chapter.chap_id" :value="chapter.chap_id">
              {{ chapter.chap_title }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Chapter ID:</label>
          <input type="text" :value="quiz.chap_id" readonly />
        </div>

      <div class="form-group">
        <label>Quiz Date:</label>
        <input type="date" v-model="quiz.quiz_date" :min="today" required/>
      </div>

        <div class="form-group">
          <label>Quiz Duration:</label>
          <div style="display: flex; gap: 10px;">
            <input type="number" v-model="quiz.quiz_duration_hours" min="0" placeholder="Hours" required />
            <input type="number" v-model="quiz.quiz_duration_minute" min="0" max="59" placeholder="Minutes" required />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit">{{ isEdit ? 'Update' : 'Add' }} Quiz</button>
          <button type="button" @click="closeModal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'QuizForm',
  props: {
    visible: Boolean,
    isEdit: Boolean,
    quizData: {
      type: Object,
      default: () => ({
        chap_id: '',
        quiz_date: '',
        quiz_duration_hours: 0,
        quiz_duration_minute: 0,
      }),
    },
    chapters: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    const today = new Date().toISOString().split('T')[0];
    return {
      quiz: { ...this.quizData },
      today,
    };
  },
  watch: {
    quizData(newVal) {
      this.quiz = { ...newVal };
    },
  },
  methods: {
    async handleSubmit() {
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        'Authentication-Token': token,
      };

      const payload = {
        chap_id: this.quiz.chap_id,
        quiz_date: this.quiz.quiz_date.split('T')[0],
        quiz_duration_hours: this.quiz.quiz_duration_hours,
        quiz_duration_minute: this.quiz.quiz_duration_minute,

      };

      try {
        if (this.isEdit) {
          await axios.put(`/api/quizzes/${this.quiz.quiz_id}`, payload, { headers });
        } else {
          await axios.post('/api/quizzes', payload, { headers });
        }

        this.$emit('submitted');
        this.closeModal();
      } catch (error) {
        console.error('Error saving quiz:', error);
        alert(error.response?.data?.message || 'Failed to save quiz.');
      }
    },
    closeModal() {
      this.$emit('close');
    },
  },
};
</script>


