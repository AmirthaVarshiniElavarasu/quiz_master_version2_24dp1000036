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

