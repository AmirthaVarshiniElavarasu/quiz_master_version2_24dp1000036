<template>
    <NavBar/>
  <div class="summary-page">
    <div v-if="isAdmin || isUser">
      <h3>Top 10 Leaderboard</h3>
      <table class="leaderboard-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>User ID</th>
            <th>Username</th>
            <th>Total Score</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in leaderboard" :key="user.id">
            <td>{{ index + 1 }}</td>
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.total_score }}</td>
          </tr>
        </tbody>
      </table>
    </div>

   <div class="chart-container">
        <div >
            <canvas id="barChart"></canvas>
        </div>
        <div >
            <canvas id="pieChart"></canvas>
        </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';

export default {
  name: 'SummaryPage',
  data() {
    return {
      isAdmin: false,
      isUser: false,
      leaderboard: [],
      barChartData: {
        labels: [],
        data: [],
        colors: []
      },
      pieChartData: {
        labels: [],
        data: [],
        colors: []
      }
    };
  },components:{NavBar},
  methods: {
    async fetchData() {
      const token = localStorage.getItem('token');
      try {
        const res = await axios.get('/api/summary_page', {
          headers: { 'Authentication-Token': token }
        });

        const { role, leaderboard, bar_data, pie_data } = res.data;

        this.isAdmin = role === 'admin';
        this.isUser = role === 'user';
        this.leaderboard = leaderboard;

        this.barChartData = {
          labels: bar_data.map(item => item.subject || item.label),
          data: bar_data.map(item => item.score || item.attempts),
          colors: bar_data.map(item => item.color)
        };

        this.pieChartData = {
          labels: pie_data.map(item => item.subject || item.month),
          data: pie_data.map(item => item.attempts),
          colors: pie_data.map(item => item.color)
        };

        this.renderCharts();
      } catch (err) {
        console.error('Error loading summary data:', err);
      }
    },
    renderCharts() {
      new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: {
          labels: this.barChartData.labels,
          datasets: [
            {
              backgroundColor: this.barChartData.colors,
              borderColor: 'black',
              borderWidth: 0.5,
              data: this.barChartData.data
            }
          ]
        },
        options: {
          plugins: {
            title: {
              display: true,
              text: 'Bar Chart Summary',
              font: {
                size: 20,
                weight: 'bold'
              }
            },
            legend: { display: false }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });

      new Chart(document.getElementById('pieChart'), {
        type: 'doughnut',
        data: {
          labels: this.pieChartData.labels,
          datasets: [
            {
              backgroundColor: this.pieChartData.colors,
              borderColor: 'black',
              borderWidth: 0.5,
              data: this.pieChartData.data
            }
          ]
        },
        options: {
          plugins: {
            title: {
              display: true,
              text: 'Pie Chart Summary',
              font: {
                size: 20,
                weight: 'bold'
              }
            },
            legend: { display: true }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }
  },
  mounted() {
    this.fetchData();
  }
};
</script>

<style scoped>


.chart-container {
    display: flex;
    justify-content: space-around;
    align-items: center;
    width: 100%;
    height: 70vh;
}

.chart-container div {
    flex: 1;
    max-width: 600px;
    height: 100%;
}


</style>
