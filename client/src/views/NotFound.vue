<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-illustration">
        <div class="astronaut">
          <div class="planet"></div>
          <div class="spaceman"></div>
        </div>
      </div>
      
      <div class="error-code">404</div>
      <h1 class="error-title">Page Not Found</h1>
      <p class="error-message">The page you're looking for seems to have floated off into space.</p>
      
      <div class="action-buttons">
        <router-link to="/" class="home-button">
          Return Home
        </router-link>
        <button @click="goBack" class="back-button">
          Go Back
        </button>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: "NotFound",
  data() {
    return {
      searchQuery: "",
      showSearch: true
    };
  },
  methods: {
    goBack() {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/');
    },
    performSearch() {
      if (this.searchQuery.trim()) {
        this.$router.push({ path: '/search', query: { q: this.searchQuery } });
      }
    }
  }
};
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: rgb(240, 251, 255);
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.not-found-content {
  max-width: 550px;
  width: 100%;
  text-align: center;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 40px 30px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.not-found-content:hover {
  transform: translateY(-5px);
}

.error-illustration {
  height: 180px;
  margin-bottom: 20px;
  position: relative;
}


.planet {
  width: 120px;
  height: 120px;
  background: linear-gradient(45deg, #3498db, #8e44ad);
  border-radius: 50%;
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: inset -20px -20px 40px rgba(0, 0, 0, 0.3), 
              0 0 20px rgba(142, 68, 173, 0.5);
  overflow: hidden;
}

.planet::before {
  content: '';
  position: absolute;
  width: 40px;
  height: 20px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  top: 30px;
  left: 20px;
  transform: rotate(-30deg);
}

.spaceman {
  position: absolute;
  width: 60px;
  height: 80px;
  top: 0;
  left: 40%;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}

.error-code {
  font-size: 6.5rem;
  font-weight: 800;
  background: linear-gradient(90deg, #FF4B2B, #FF416C, #6a11cb, #2575fc);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 300% 300%;
  animation: gradientText 5s ease infinite;
  margin: 0 0 10px 0;
  line-height: 1;
  letter-spacing: -2px;
  text-shadow: 4px 4px 0px rgba(0, 0, 0, 0.1);
}

@keyframes gradientText {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.error-title {
  font-size: 2.4rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 15px 0;
}

.error-message {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 35px;
}

.home-button, .back-button {
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.home-button {
  background: linear-gradient(45deg, #6a11cb, #2575fc);
  color: white;
  border: none;
  text-decoration: none;
  box-shadow: 0 6px 15px rgba(106, 17, 203, 0.3);
}

.home-button:hover {
  background: linear-gradient(45deg, #5a0fb0, #1e64d9);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(106, 17, 203, 0.4);
}

.back-button {
  background-color: white;
  color: #6a11cb;
  border: 2px solid #6a11cb;
  box-shadow: 0 4px 12px rgba(106, 17, 203, 0.1);
}

.back-button:hover {
  background-color: rgba(106, 17, 203, 0.08);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(106, 17, 203, 0.2);
}

.button-icon {
  font-size: 1.1rem;
}

.search-section {
  margin-top: 25px;
  width: 100%;
}

.search-label {
  font-size: 1rem;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.search-container {
  display: flex;
  max-width: 90%;
  margin: 0 auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.search-input {
  flex: 1;
  padding: 14px 18px;
  border: none;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

.search-input:focus {
  box-shadow: inset 0 0 0 2px #6a11cb;
}

.search-button {
  width: 50px;
  background: linear-gradient(45deg, #6a11cb, #2575fc);
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-button:hover {
  background: linear-gradient(45deg, #5a0fb0, #1e64d9);
}

.search-icon {
  font-size: 1.2rem;
}

@media (max-width: 640px) {
  .not-found-content {
    padding: 30px 20px;
  }
  
  .error-illustration {
    height: 140px;
  }
  
  .planet {
    width: 100px;
    height: 100px;
  }
  
  .spaceman {
    width: 50px;
    height: 60px;
  }
  
  .error-code {
    font-size: 4.5rem;
  }
  
  .error-title {
    font-size: 1.8rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .home-button, .back-button {
    width: 100%;
  }
}
</style>