<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-box">
      <h2>{{ isEdit ? 'Edit' : 'Add' }} Question</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Quiz ID:</label>
          <input type="text" v-model="question.quiz_id" readonly />
        </div>

        <div class="form-group">
          <label>Question Statement:</label>
          <textarea v-model="question.ques_statement" required></textarea>
        </div>

        <div class="form-group">
          <label>Options (Min 2):</label>
          <div v-for="(opt, index) in options" :key="index" class="option-item">
            <input type="text" v-model="options[index]" required />
            <input
              type="radio"
              :value="index"
              v-model="correctOptionIndex"
              :name="'correctOption'"
            /> Correct
            <button type="button" @click="removeOption(index)" v-if="options.length > 2">
              Remove
            </button>
          </div>
          <button type="button" @click="addOption">Add Option</button>
        </div>

        <div class="form-actions">
          <button type="submit">{{ isEdit ? 'Update' : 'Add' }} Question</button>
          <button type="button" @click="closeModal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'QuestionForm',
  props: {
    visible: Boolean,
    isEdit: Boolean,
    questionData: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      question: { ...this.questionData },
      options: this.questionData.options.map(opt => opt.op_statement || ''),
      correctOptionIndex: this.questionData.correct_option
        ? this.questionData.options.findIndex(opt => opt.op_id === this.questionData.correct_option.op_id)
        : 0
    };
  },
  watch: {
    questionData(newVal) {
      this.question = { ...newVal };
      this.options = newVal.options.map(opt => opt.op_statement || '');
      this.correctOptionIndex = newVal.correct_option
        ? newVal.options.findIndex(opt => opt.op_id === newVal.correct_option.op_id)
        : 0;
    }
  },
  methods: {
    addOption() {
      this.options.push('');
    },
    removeOption(index) {
      this.options.splice(index, 1);
      if (this.correctOptionIndex === index || this.correctOptionIndex >= this.options.length) {
        this.correctOptionIndex = 0;
      }
    },
    async handleSubmit() {
      if (this.options.length < 2) {
        alert('At least 2 options are required.');
        return;
      }

      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        'Authentication-Token': token,
      };

      const payload = {
        ques_statement: this.question.ques_statement,
        quiz_id: this.question.quiz_id,
        correct_option_id: null,
        options: this.options
      };

      try {
        if (this.isEdit) {
          payload.correct_option_id = this.question.options[this.correctOptionIndex]?.op_id;
          await axios.put(`/api/questions/${this.question.ques_id}`, payload, { headers });
        } else {
          payload.correct_option = this.options[this.correctOptionIndex];
          await axios.post('/api/questions', payload, { headers });
        }

        this.$emit('submitted');
        this.closeModal();
      } catch (err) {
        console.error('Error submitting question:', err);
        alert('Failed to save question.');
      }
    },
    closeModal() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-box {
  background: white;
  padding: 20px;
  border-radius: 10px;
  min-width: 450px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-weight: bold;
}

.form-group input,
textarea {
  width: 100%;
  padding: 6px;
  box-sizing: border-box;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
