import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://apdqbeaglgbftfpmklrn.supabase.co'
const SUPABASE_KEY = 'sb_publishable_NHujqEWU8y2zAWPWrDfAZA_3rve70za'

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// Helper to get settings
export async function getSettings() {
    const { data, error } = await supabase.from('settings').select('*')
    if (error) return {}
    return data.reduce((acc, curr) => {
        acc[curr.key] = curr.value
        return acc
    }, {})
}

// Initial state
const state = {
    cart: [],
    settings: {},
    categories: []
}

async function init() {
    state.settings = await getSettings()
    renderShopStatus()
    loadCategories()
}

function renderShopStatus() {
    const statusEl = document.getElementById('shopStatus')
    if (!statusEl) return

    const isOpen = state.settings.shop_status === 'open'

    if (isOpen) {
        statusEl.innerHTML = `
            <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            Now Open & Taking Orders
        `
        statusEl.className = "inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-700 rounded-full font-semibold text-sm"
    } else {
        statusEl.innerHTML = `
            <span class="w-2 h-2 bg-rose-500 rounded-full"></span>
            Shop Closed - Back Soon
        `
        statusEl.className = "inline-flex items-center gap-2 px-4 py-2 bg-rose-100 text-rose-700 rounded-full font-semibold text-sm"
    }
}

async function loadCategories() {
    const { data, error } = await supabase.from('categories').select('*')
    if (error) return

    const container = document.getElementById('categoryContainer')
    if (!container) return

    container.innerHTML = data.map(cat => `
        <div class="glass-card p-6 flex flex-col items-center gap-4 hover:scale-105 hover:bg-white transition-all cursor-pointer">
            <div class="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center text-3xl">🍲</div>
            <span class="font-bold text-slate-800">${cat.name}</span>
        </div>
    `).join('')
}

document.addEventListener('DOMContentLoaded', init)
