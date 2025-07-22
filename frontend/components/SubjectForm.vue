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
