<template>
    <div class="not-found-container">
      <div class="not-found-content">
        <h1 class="error-code">404</h1>
        <div class="error-divider"></div>
        <h2 class="error-title">Page Not Found</h2>
        <p class="error-message">Oops! The page you're looking for doesn't exist or has been moved.</p>
        <router-link to="/" class="home-button">
          <span class="button-icon">←</span> Return to Homepage
        </router-link>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "NotFound"
  };
  </script>
  
  <style scoped>
  .not-found-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f8f9fa;
    padding: 20px;
  }
  
  .not-found-content {
    max-width: 500px;
    text-align: center;
    background-color: white;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  }
  
  .error-code {
    font-size: 6rem;
    font-weight: 700;
    color: darkcyan;
    margin: 0;
    line-height: 1;
  }
  
  .error-divider {
    height: 4px;
    width: 60px;
    background-color: darkcyan;
    margin: 20px auto;
    border-radius: 2px;
  }
  
  .error-title {
    font-size: 2rem;
    font-weight: 600;
    color: #424242;
    margin: 0 0 15px 0;
  }
  
  .error-message {
    font-size: 1.1rem;
    color: #757575;
    margin-bottom: 30px;
    line-height: 1.5;
  }
  
  .home-button {
    display: inline-flex;
    align-items: center;
    background-color: darkcyan;
    color: white;
    font-weight: 500;
    padding: 12px 24px;
    border-radius: 50px;
    text-decoration: none;
    transition: all 0.3s ease;
  }
  
  .home-button:hover {
    background-color: darkgreen;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(92, 107, 192, 0.2);
  }
  
  .button-icon {
    margin-right: 8px;
    font-size: 1.1rem;
  }
  
  @media (max-width: 600px) {
    .not-found-content {
      padding: 30px;
    }
    
    .error-code {
      font-size: 4rem;
    }
    
    .error-title {
      font-size: 1.5rem;
    }
  }
  </style>