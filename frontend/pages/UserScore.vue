<template>
    <NavBar/>
  <div class="score-container">
    <h2>Quiz Scores</h2>
    <table class="user-score-table">
      <thead>
        <tr>
          <th>Quiz Name</th>
          <th>No. of Questions</th>
          <th>Date</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="score in scores" :key="score.score_id">
          <td>{{ score.quiz_name }}</td>
          <td>{{ score.No_of_question }}</td>
          <td>{{ formatDate(score.score_time_stamp) }}</td>
          <td>{{ score.score_total }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from "axios";
import NavBar from "@/components/NavBar.vue";


export default {
  name: "UserScore",
  data() {
    return {
      scores: [],
    };
  },
  mounted() {
    this.fetchScores();
  },components:{NavBar},
  methods: {
    async fetchScores() {
      const token = localStorage.getItem("token");
      const userId = localStorage.getItem("user_id"); // or from route params
      try {
        const response = await axios.get(`/api/score_page/${userId}`, {
          headers: {
            "Authentication-Token": token,
          },
        });
        this.scores = response.data || [];
      } catch (error) {
        console.error("Error fetching scores:", error);
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString("en-GB"); // dd/mm/yyyy hh:mm
    },
  },
};
</script>

<style scoped>
.score-container {
  text-align: center;
}
.user-score-table {
  margin: auto;
  border-collapse: collapse;
  width: 80%;
}
.user-score-table th,
.user-score-table td {
  border: 1px solid #ddd;
  padding: 8px;
}
.user-score-table th {
  background-color: #f2f2f2;
}
</style>
