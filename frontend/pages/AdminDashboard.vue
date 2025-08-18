<template>
  <NavBar />
  <div class="dashboard">
    <h2 class="text-center">Welcome, {{ username }}</h2>
    <div v-if="subjects.length === 0" class="no-data">No subjects found.</div>

    <div v-for="subject in subjects" :key="subject.sub_id" class="subject-card">
      <h3>{{ subject.sub_name }}</h3>
      <button @click="editSubject(subject)">Edit</button>
      <button @click="deleteSubject(subject)">Delete</button>

      <button @click="toggleDescription(subject.sub_id)">
        {{ visibleDescriptions.includes(subject.sub_id) ? 'Hide' : 'Show' }} Details
      </button>

      <div v-show="visibleDescriptions.includes(subject.sub_id)">
        <p><strong>Subject Description:</strong> {{ subject.sub_Description }}</p>
      </div>

      <table class="chapter-table">
        <thead>
          <tr>
            <th>Chapter Title</th>
            <th>No. of Quizzes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="chapter in chaptersBySubject(subject.sub_id)"
            :key="chapter.chap_id"
          >
            <td>{{ chapter.chap_title }}</td>
            <td>{{ getQuizCount(chapter.chap_id) }}</td>
            <td>
              <button @click="editChapter(chapter)">Edit</button>
              <button @click="deleteChapter(chapter)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <button @click="addChapter(subject.sub_id)">Add Chapter</button>
      <hr />
    </div>
    <button @click="addSubject()">Add Subject</button>
  </div>
  <SubjectForm :visible="showSubjectForm" :isEdit="isEditingSubject" :subjectData="selectedSubject" @close="showSubjectForm = false" @submitted="handleSubjectSubmit"/>
  <ChapterForm :visible="showChapterForm" :isEdit="isEditingChapter" :ChapterData="selectedChapter" @close="showChapterForm = false" @submitted="handleChapterSubmit"/>
</template>

<script>
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';
import SubjectForm from '@/components/SubjectForm.vue';
import ChapterForm from '@/components/ChapterForm.vue';


export default {
  name: 'AdminDashboard',
  data() {
    return {
      username: '',
      subjects: [],
      chapters: [],
      visibleDescriptions: [],
      quizzes: [],
      // Subject
      showSubjectForm: false,
      isEditingSubject: false,
      selectedSubject: null,
      // Chapter
      showChapterForm: false,
      isEditingChapter: false,
      selectedChapter: null,


    };
  },
  components: {
    NavBar,
    SubjectForm,
    ChapterForm
  },
  methods: {
    async fetchData() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/admin_dashboard', {
          headers: {
            'Authentication-Token': token,
          },
        });
        this.subjects = res.data.subjects || [];
        this.chapters = res.data.chapters || [];
        this.quizzes = res.data.quizzes || [];
        this.username = res.data.user || 'Admin';
      } catch (err) {
        console.error('Failed to load admin data', err);
        this.$router.push('/login'); // Redirect if token is invalid
      }
    },
    chaptersBySubject(sub_id) {
      return this.chapters.filter((c) => c.sub_id === sub_id);
    },
    getQuizCount(chap_id) {
      return this.quizzes.filter((q) => q.chap_id === chap_id).length;
    },
    toggleDescription(subId) {
      const idx = this.visibleDescriptions.indexOf(subId);
      if (idx > -1) {
        this.visibleDescriptions.splice(idx, 1);
      } else {
        this.visibleDescriptions.push(subId);
      }
    },
    deleteChapter(chapter) {
      if (confirm(`Are you sure you want to delete "${chapter.chap_title} ${chapter.chap_id}"?`)) {
        const token = localStorage.getItem('token');
        axios.delete(`/api/chapters/${chapter.chap_id}`, {
            headers: {
              'Authentication-Token': token,
            },
          })
          .then(() => {
            this.fetchData();
          })
          .catch((err) => {
            console.error('Failed to delete chapter:', err);
              if (err.response && err.response.data && err.response.data.message) {
                   alert(`Error: ${err.response.data.message}`);} 
              else {
                    alert('Error deleting chapter.');
                  }
          });
      }
    },
    addChapter(sub_id) {
      this.selectedChapter = { sub_id:sub_id, chap_title: '', chap_description: ''};
      this.isEditingChapter = false;
      this.showChapterForm = true;

    },
    editChapter(chapter) {
      this.selectedChapter = { ...chapter };
      this.isEditingChapter = true;
      this.showChapterForm = true;
    },
    handleChapterSubmit() {
      this.showChapterForm = false;
      this.fetchData();
    },
    handleSubjectSubmit() {
     this.showSubjectForm = false;
     this.fetchData(); // Refresh subjects after adding/updating
    },
    addSubject() {
      this.selectedSubject = { sub_name: '', sub_Description: '', sub_quiz_descrip: ''};
      this.isEditingSubject = false;
      this.showSubjectForm = true;

    },
    editSubject(subject) { this.selectedSubject = { ...subject }; 
    this.isEditingSubject = true; 
    this.showSubjectForm = true;
    },
    deleteSubject(subject) {
      if (confirm(`Are you sure you want to delete "${subject.sub_name} ${subject.sub_id}"?`)) {
        const token = localStorage.getItem('token');
        axios.delete(`/api/subject/${subject.sub_id}`, {
            headers: {
              'Authentication-Token': token,
            },
          })
          .then(() => {
            this.fetchData();
          })
          .catch((err) => {
            console.error('Failed to delete subject:', err);
              if (err.response && err.response.data && err.response.data.message) {
                   alert(`Error: ${err.response.data.message}`);} 
              else {
                    alert('Error deleting subject.');
                  }
          });
      }
    }
  },
  mounted() {
    this.fetchData();
  },
};
</script>

