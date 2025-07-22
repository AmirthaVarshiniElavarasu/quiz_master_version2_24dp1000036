<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-box">
      <h2>{{ isEdit ? 'Edit' : 'Add' }} Chapter</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Subject ID:</label>
          <input type="text" v-model="chapter.sub_id" readonly />
        </div>
        <div class="form-group">
          <label>Chapter Title:</label>
          <input type="text" v-model="chapter.chap_title" required />
        </div>
        <div class="form-group">
          <label>Description:</label>
          <textarea v-model="chapter.chap_description" required></textarea>
        </div>
        <div class="form-actions">
          <button type="submit">{{ isEdit ? 'Update' : 'Add' }} Chapter</button>
          <button type="button" @click="closeModal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ChapterForm',
  props: {
    visible: Boolean,
    isEdit: Boolean,
    ChapterData: {
      type: Object,
      default: () => ({
        sub_id: null,
        chap_title: '',
        chap_description: ''
      })
    }
  },
  data() {
    return {
      chapter: { ...this.ChapterData }
    };
  },
  watch: {
    ChapterData(newVal) {
      this.chapter = { ...newVal };
    }
  },
  methods: {
    async handleSubmit() {
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        'Authentication-Token': token,
      };

      try {
        if (this.isEdit) {
          // PUT request with chapter ID
          await axios.put(`/api/chapters/${this.chapter.chap_id}`, this.chapter, { headers });
        } else {
          // POST request to add new chapter
          await axios.post('/api/chapters', this.chapter, { headers });
        }

        this.$emit('submitted'); // Notify parent to reload data
        this.closeModal();
      } catch (error) {
        console.error('Error saving chapter:', error);
        alert('Failed to save chapter. Please try again.');
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
  min-width: 400px;
}
.form-group {
  margin-bottom: 12px;
}
.form-group label {
  display: block;
  font-weight: bold;
}
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 6px;
  box-sizing: border-box;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
