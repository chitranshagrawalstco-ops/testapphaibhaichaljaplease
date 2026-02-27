import { supabase, getSettings } from './main.js'

let cart = []
let menuItems = []
let categories = []
let settings = {}

const elements = {
    menuGrid: document.getElementById('menuGrid'),
    catFilter: document.getElementById('categoryFilter'),
    cartBtn: document.getElementById('cartBtn'),
    cartSidebar: document.getElementById('cartSidebar'),
    cartPanel: document.getElementById('cartPanel'),
    cartOverlay: document.getElementById('cartOverlay'),
    closeCart: document.getElementById('closeCart'),
    cartItems: document.getElementById('cartItems'),
    cartTotal: document.getElementById('cartTotal'),
    cartCount: document.getElementById('cartCount'),
    toast: document.getElementById('toast'),
    checkoutBtn: document.getElementById('checkoutBtn')
}

async function init() {
    settings = await getSettings()
    await loadData()
    renderCategories()
    renderMenu('all')
    setupCart()
}

async function loadData() {
    const { data: items } = await supabase.from('menu_items').select('*').eq('is_available', true)
    const { data: cats } = await supabase.from('categories').select('*')
    menuItems = items || []
    categories = cats || []
}

function renderCategories() {
    elements.catFilter.innerHTML = `
        <button class="px-6 py-2 bg-primary-600 text-white rounded-full font-semibold shadow-md whitespace-nowrap active-cat" data-category="all">All</button>
        ${categories.map(cat => `
            <button class="px-6 py-2 bg-white text-slate-600 rounded-full font-semibold shadow-sm whitespace-nowrap hover:bg-primary-50 transition-all border border-transparent" data-category="${cat.id}">${cat.name}</button>
        `).join('')}
    `

    // Category Filter Logic
    elements.catFilter.querySelectorAll('button').forEach(btn => {
        btn.onclick = () => {
            elements.catFilter.querySelectorAll('button').forEach(b => {
                b.className = "px-6 py-2 bg-white text-slate-600 rounded-full font-semibold shadow-sm whitespace-nowrap hover:bg-primary-50 transition-all border border-transparent"
            })
            btn.className = "px-6 py-2 bg-primary-600 text-white rounded-full font-semibold shadow-md whitespace-nowrap"
            renderMenu(btn.dataset.category)
        }
    })
}

function renderMenu(categoryId) {
    const filtered = categoryId === 'all'
        ? menuItems
        : menuItems.filter(item => item.category_id == categoryId)

    elements.menuGrid.innerHTML = filtered.map(item => `
        <div class="glass-card overflow-hidden group hover:shadow-2xl transition-all duration-500 bg-white">
            <div class="relative h-48 overflow-hidden">
                <img src="${item.image_path || 'https://via.placeholder.com/400x300?text=Delicious+Food'}" 
                     alt="${item.name}" 
                     class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700">
                <div class="absolute top-4 right-4 px-3 py-1 bg-white/90 backdrop-blur rounded-full text-xs font-bold text-slate-800 shadow-sm">
                    ${item.is_non_veg ? '🔴 Non-Veg' : '🟢 Veg'}
                </div>
            </div>
            
            <div class="p-6 space-y-4">
                <div class="flex justify-between items-start">
                    <h3 class="text-xl font-bold text-slate-900">${item.name}</h3>
                    <span class="text-xl font-bold text-primary-600">₹${item.price}</span>
                </div>
                <p class="text-slate-500 text-sm line-clamp-2">${item.description || 'Authentic street style preparation.'}</p>
                <button class="add-to-cart w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-primary-600 transition-colors flex items-center justify-center gap-2" 
                        data-id="${item.id}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                    Add to Basket
                </button>
            </div>
        </div>
    `).join('')

    // Add To Cart Listeners
    elements.menuGrid.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.onclick = () => addToCart(btn.dataset.id)
    })
}

function setupCart() {
    elements.cartBtn.onclick = () => toggleCart(true)
    elements.closeCart.onclick = () => toggleCart(false)
    elements.cartOverlay.onclick = () => toggleCart(false)
}

function toggleCart(open) {
    elements.cartSidebar.style.pointerEvents = open ? 'auto' : 'none'
    elements.cartOverlay.style.opacity = open ? '1' : '0'
    elements.cartPanel.style.transform = open ? 'translateX(0)' : 'translateX(100%)'
}

function addToCart(id) {
    const item = menuItems.find(i => i.id == id)
    const existing = cart.find(i => i.id == id)

    if (existing) {
        existing.quantity += 1
    } else {
        cart.push({ ...item, quantity: 1 })
    }

    updateCartUI()
    showToast(`Added ${item.name}!`)
}

function updateCartUI() {
    elements.cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0)

    if (cart.length === 0) {
        elements.cartItems.innerHTML = `<div class="text-center py-20 text-slate-400">Basket is empty</div>`
        elements.cartTotal.textContent = `₹0.00`
        return
    }

    elements.cartItems.innerHTML = cart.map(item => `
        <div class="flex gap-4 items-center">
            <div class="w-16 h-16 rounded-xl overflow-hidden bg-slate-100">
                <img src="${item.image_path || 'https://via.placeholder.com/100'}" class="w-full h-full object-cover">
            </div>
            <div class="flex-1">
                <h4 class="font-bold text-slate-900">${item.name}</h4>
                <div class="flex items-center gap-4 mt-2">
                    <div class="flex items-center bg-slate-100 rounded-lg">
                        <button class="px-2 py-1 text-slate-500 hover:text-slate-900" onclick="changeQty(${item.id}, -1)">-</button>
                        <span class="px-2 font-bold text-sm">${item.quantity}</span>
                        <button class="px-2 py-1 text-slate-500 hover:text-slate-900" onclick="changeQty(${item.id}, 1)">+</button>
                    </div>
                    <span class="text-primary-600 font-bold">₹${item.price * item.quantity}</span>
                </div>
            </div>
        </div>
    `).join('')

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    elements.cartTotal.textContent = `₹${total.toFixed(2)}`
}

window.changeQty = (id, delta) => {
    const item = cart.find(i => i.id == id)
    item.quantity += delta
    if (item.quantity <= 0) {
        cart = cart.filter(i => i.id != id)
    }
    updateCartUI()
}

function showToast(msg) {
    elements.toast.textContent = msg
    elements.toast.style.opacity = '1'
    setTimeout(() => elements.toast.style.opacity = '0', 2000)
}

elements.checkoutBtn.onclick = async () => {
    if (cart.length === 0) return

    // Check shop status first
    const currentSettings = await getSettings()
    if (currentSettings.shop_status !== 'open') {
        alert("Sorry, the shop just closed! Please try again later.")
        return
    }

    const orderText = cart.map(i => `${i.name} x ${i.quantity}`).join('%0A')
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    const phone = settings.phone?.replace(/\D/g, '') || ''
    const msg = `New Order from StreetBite Website:%0A------------------%0A${orderText}%0A------------------%0ATotal: ₹${total}%0A%0APlease confirm my order!`

    window.open(`https://wa.me/${phone}?text=${msg}`, '_blank')
}

document.addEventListener('DOMContentLoaded', init)
