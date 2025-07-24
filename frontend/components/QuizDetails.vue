<template>
  <div class="modal-overlay">
    <div class="modal-box">
      <table>
      <tbody>
        <tr>
          <th>Quiz ID:</th>
          <td><input type="text" :value="quiz.quiz_id" readonly /></td>
        </tr>
        <tr>
          <th>Subject:</th>
          <td><input type="text" :value="subject.sub_name" readonly /></td>
        </tr>
        <tr>
          <th>Subject Description:</th>
          <td><input type="text" :value="subject.sub_Description" readonly /></td>
        </tr>
        <tr>
          <th>Chapter:</th>
          <td><input type="text" :value="chapter.chap_title" readonly /></td>
        </tr>
        <tr>
          <th>Chapter Description:</th>
          <td><input type="text" :value="chapter.chap_description" readonly /></td>
        </tr>
        <tr>
          <th>Number of Questions:</th>
          <td><input type="text" :value="quiz.total_questions" readonly /></td>
        </tr>
        <tr>
          <th>Scheduled Date:</th>
          <td>
            <input type="text" :value="formatDateTime(quiz.quiz_date)" readonly />
          </td>
        </tr>
        <tr>
          <th>Duration (minutes):</th>
          <td><input type="text" :value="quiz.quiz_time" readonly /></td>
        </tr>
        <tr>
          <td colspan="2" style="text-align: right;">
            <button @click="$emit('close')">Close</button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script>
export default {
  name: 'QuizDetails',
  props: {
    quiz: Object,
    subject: Object,
    chapter: Object,
  },
  methods: {
    formatDateTime(datetime) {
      if (!datetime) return '';
      const date = new Date(datetime);
      return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    },
  },
};
</script>
