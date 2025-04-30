// Common JS functionality for all pages

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltips = document.querySelectorAll('.tooltip');
  
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      
      if (targetId === '#') return;
      
      document.querySelector(targetId).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
  
  // Animated elements
  const animatedElements = document.querySelectorAll('.fade-in');
  
  function checkIfInView() {
    animatedElements.forEach(element => {
      const elementTop = element.getBoundingClientRect().top;
      const elementVisible = 150; // Element becomes visible 150px from the viewport top
      
      if (elementTop < window.innerHeight - elementVisible) {
        element.classList.add('active');
      }
    });
  }
  
  // Initial check
  checkIfInView();
  
  // Check again on scroll
  window.addEventListener('scroll', checkIfInView);
  
  // Mobile menu toggle
  const mobileMenuButton = document.querySelector('.mobile-menu-button');
  const navLinks = document.querySelector('.navbar-nav');
  
  if (mobileMenuButton) {
    mobileMenuButton.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }
  
  // Feature card hover effects
  const featureCards = document.querySelectorAll('.feature-card');
  
  featureCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.classList.add('active');
    });
    
    card.addEventListener('mouseleave', () => {
      card.classList.remove('active');
    });
  });
  
  // Pricing card hover effects
  const pricingCards = document.querySelectorAll('.pricing-card');
  
  pricingCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.classList.add('active');
    });
    
    card.addEventListener('mouseleave', () => {
      card.classList.remove('active');
    });
  });
});

// Utility functions
function showAlert(message, type = 'info') {
  const alertElement = document.createElement('div');
  alertElement.className = `alert alert-${type}`;
  alertElement.textContent = message;
  
  // Create close button
  const closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.className = 'close';
  closeButton.innerHTML = '&times;';
  closeButton.addEventListener('click', () => {
    alertElement.remove();
  });
  
  alertElement.prepend(closeButton);
  
  // Add to document
  document.body.appendChild(alertElement);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    alertElement.remove();
  }, 5000);
}

function showLoading(message = 'Loading...') {
  const loadingElement = document.createElement('div');
  loadingElement.className = 'loading-overlay';
  loadingElement.innerHTML = `
    <div class="loading-content">
      <div class="spinner">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      <p>${message}</p>
    </div>
  `;
  
  document.body.appendChild(loadingElement);
  
  return () => {
    loadingElement.remove();
  };
}
