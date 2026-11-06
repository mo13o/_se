const KEY = "booknest-cart-v1";
export function getCart(){try{return JSON.parse(localStorage.getItem(KEY))||[]}catch{return[]}}
export function saveCart(cart){localStorage.setItem(KEY,JSON.stringify(cart));window.dispatchEvent(new CustomEvent("cartchange",{detail:cart}))}
export function addToCart(book,quantity=1){const cart=getCart(),old=cart.find(x=>x.id===book.id);if(old)old.quantity=Math.min(old.quantity+quantity,book.stock,99);else cart.push({id:book.id,title:book.title,author:book.author,price:book.price,stock:book.stock,image_url:book.image_url,quantity:Math.min(quantity,book.stock)});saveCart(cart)}
export function cartCount(){return getCart().reduce((s,x)=>s+x.quantity,0)}
export function updateCartBadge(){const count=cartCount();document.querySelectorAll(".cart-badge").forEach(x=>x.textContent=count);document.querySelectorAll(".cart-link").forEach(x=>x.setAttribute("aria-label",`購物車，${count} 件商品`))}
window.addEventListener("cartchange",updateCartBadge);
