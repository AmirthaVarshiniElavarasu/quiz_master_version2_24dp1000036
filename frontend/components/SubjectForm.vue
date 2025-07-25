<template>

  <div v-if="visible" class="modal-overlay">
    <div class="modal-box">
      <h2>{{ isEdit ? 'Edit' : 'Add' }} Subject</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Subject Name:</label>
          <input type="text" v-model="subject.sub_name" required />
        </div>
        <div class="form-group">
          <label>Description:</label>
          <textarea v-model="subject.sub_Description" required></textarea>
        </div>
        <div class="form-actions">
          <button type="submit">{{ isEdit ? 'Update' : 'Add' }} Subject</button>
          <button type="button" @click="closeModal">Cancel</button>
        </div>
      </form>
    </div>
  </div>

</template>

<script>
import axios from 'axios';

export default {
  name: 'SubjectForm',
  props: {
    visible: Boolean,
    isEdit: Boolean,
    subjectData: {
      type: Object,
      default: () => ({
        sub_name: '',
        sub_Description: ''
      })
    }
  },
  data() {
    return {
      subject: { ...this.subjectData }
    };
  },
  watch: {
    subjectData(newVal) {
      this.subject = { ...newVal };
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
            // PUT request for updating an existing subject
            await axios.put(`/api/subject/${this.subject.sub_id}`, this.subject, { headers });
            } else {
            // POST request for creating a new subject
            await axios.post(`/api/subject`, this.subject, { headers });
            }

            this.$emit('submitted'); // Notify parent
            this.closeModal();
        } catch (error) {
            console.error('Error submitting subject:', error);
            alert('Failed to save subject. Please try again.');
        }
        },
    closeModal() {
      this.$emit('close');
    }
  }
};
</script>


