let cart = JSON.parse(localStorage.getItem('cart')) || [];
let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];

function updateCounts() {
    const cartCount = cart.reduce((total, item) => total + item.quantity, 0);
    const wishlistCount = wishlist.length;
    
    const cartEl = document.getElementById('cart-count');
    const wishEl = document.getElementById('wishlist-count');
    
    if(cartEl) cartEl.innerText = cartCount;
    if(wishEl) wishEl.innerText = wishlistCount;
}

function addToCart(id, name, price, image) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCounts();
    showToast('Added to Cart', name + ' has been added to your cart.');
}

function toggleWishlist(id, name, price, image) {
    const index = wishlist.findIndex(item => item.id === id);
    if (index > -1) {
        wishlist.splice(index, 1);
        showToast('Removed from Wishlist', name + ' removed.');
    } else {
        wishlist.push({ id, name, price, image });
        showToast('Added to Wishlist', name + ' saved for later!');
    }
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
    updateCounts();
    // Optional: toggle icon color on page if we wanted to
}

function showToast(title, message) {
    const toastHtml = `
    <div class="toast-container position-fixed bottom-0 start-0 p-3" style="z-index: 1100">
      <div class="toast show bg-dark text-white border-0 shadow-lg" role="alert">
        <div class="toast-header bg-dark text-white border-secondary">
          <strong class="me-auto text-primary"><i class="bi bi-check-circle-fill"></i> ${title}</strong>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">${message}</div>
      </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', toastHtml);
    setTimeout(() => {
        const toastEl = document.body.lastElementChild;
        if(toastEl.classList.contains('toast-container')) toastEl.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    updateCounts();
});
