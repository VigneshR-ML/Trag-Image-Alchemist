// Stripe Integration

document.addEventListener('DOMContentLoaded', function() {
  // Find all purchase buttons
  const purchaseButtons = document.querySelectorAll('.purchase-btn');
  
  purchaseButtons.forEach(button => {
    button.addEventListener('click', async (event) => {
      event.preventDefault();
      
      // Get the price ID from the button's data attribute
      const priceId = button.getAttribute('data-price-id');
      
      if (!priceId) {
        showAlert('Invalid price ID', 'danger');
        return;
      }
      
      const hideLoading = showLoading('Redirecting to checkout...');
      
      try {
        // Create checkout session
        const response = await fetch('/create-checkout-session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            priceId: priceId
          }),
        });
        
        const session = await response.json();
        
        if (session.error) {
          hideLoading();
          showAlert(session.error, 'danger');
          return;
        }
        
        // Redirect to Stripe Checkout
        const stripe = Stripe(stripePublishableKey);
        const result = await stripe.redirectToCheckout({
          sessionId: session.id,
        });
        
        if (result.error) {
          hideLoading();
          showAlert(result.error.message, 'danger');
        }
      } catch (error) {
        hideLoading();
        showAlert('An error occurred. Please try again.', 'danger');
        console.error('Error:', error);
      }
    });
  });
});

// Utility function to show alerts (available globally)
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

// Utility function to show loading overlay (available globally)
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
