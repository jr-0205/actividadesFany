const state = { products: [], cart: new Map(), category: 'Todos', search: '' };
const $ = (s) => document.querySelector(s);
const money = (n) => new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN',maximumFractionDigits:0}).format(n);
const iconMap = {ssd:'▣',keyboard:'⌨',mouse:'◒',webcam:'◉',hub:'⌘',battery:'▰',headphones:'∩',router:'⌁'};

function toast(message, error=false){const el=$('#toast');el.textContent=message;el.className='toast'+(error?' error':'');requestAnimationFrame(()=>el.classList.add('show'));setTimeout(()=>el.classList.remove('show'),2600)}

async function api(url, options={}){
  const res = await fetch(url,{headers:{'Content-Type':'application/json'},...options});
  const data = await res.json();
  if(!res.ok) throw new Error(data.error || 'Ocurrió un error');
  return data;
}

async function loadAll(){
  const [products, stats, sales] = await Promise.all([api('/api/products'),api('/api/stats'),api('/api/sales')]);
  state.products=products; renderFilters(); renderProducts(); renderInventory(); renderStats(stats); renderSales(sales); renderCart();
}

function renderStats(s){
  $('#metricProducts').textContent=s.products; $('#metricUnits').textContent=s.units; $('#metricSales').textContent=s.sales_count; $('#metricRevenue').textContent=money(s.revenue);
}

function renderFilters(){
  const cats=['Todos',...new Set(state.products.map(p=>p.category))];
  $('#filters').innerHTML=cats.map(c=>`<button data-category="${c}" class="${state.category===c?'active':''}">${c}</button>`).join('');
  $('#filters').querySelectorAll('button').forEach(btn=>btn.addEventListener('click',()=>{state.category=btn.dataset.category;renderFilters();renderProducts()}));
}

function filteredProducts(){
  return state.products.filter(p=>(state.category==='Todos'||p.category===state.category)&&(!state.search||`${p.name} ${p.sku} ${p.description}`.toLowerCase().includes(state.search)));
}

function renderProducts(){
  const products=filteredProducts();
  $('#productGrid').innerHTML=products.length?products.map(p=>`
    <article class="product-card">
      <div class="product-visual">${p.featured?'<span class="featured-tag">DESTACADO</span>':''}<span class="tech-icon">${iconMap[p.icon]||'◇'}</span></div>
      <div class="product-body">
        <div class="product-meta"><span>${p.sku} · ${p.category}</span><span class="${p.stock<=15?'stock-low':'stock-ok'}">${p.stock} disp.</span></div>
        <h3 title="${p.name}">${p.name}</h3><p>${p.description}</p>
        <div class="product-buy"><div><strong>${money(p.price)}</strong><small> PRECIO SIMULADO</small></div><button class="add-btn" data-add="${p.id}" ${p.stock===0?'disabled':''}>+</button></div>
      </div>
    </article>`).join(''):'<p class="empty-sale">No se encontraron productos.</p>';
  $('#productGrid').querySelectorAll('[data-add]').forEach(b=>b.addEventListener('click',()=>addToCart(Number(b.dataset.add))));
}

function addToCart(id){
  const p=state.products.find(x=>x.id===id); if(!p||p.stock===0)return;
  const qty=state.cart.get(id)||0; if(qty>=p.stock){toast('No hay más unidades disponibles.',true);return}
  state.cart.set(id,qty+1);renderCart();toast(`${p.name} agregado`);
}
function changeQty(id,delta){const p=state.products.find(x=>x.id===id);let qty=(state.cart.get(id)||0)+delta;if(qty<=0)state.cart.delete(id);else if(qty<=p.stock)state.cart.set(id,qty);else toast('Stock máximo alcanzado.',true);renderCart()}
function renderCart(){
  const entries=[...state.cart.entries()]; const count=entries.reduce((a,[,q])=>a+q,0); $('#cartCount').textContent=count;
  $('#cartItems').innerHTML=entries.length?entries.map(([id,q])=>{const p=state.products.find(x=>x.id===id);return `<div class="cart-item"><div><strong>${p.name}</strong><small>${money(p.price)} c/u</small></div><div class="cart-controls"><button data-minus="${id}">−</button><span>${q}</span><button data-plus="${id}">+</button></div></div>`}).join(''):'<div class="empty-state"><strong>Tu carrito está vacío</strong><p>Agrega productos desde el catálogo.</p></div>';
  const total=entries.reduce((sum,[id,q])=>sum+state.products.find(x=>x.id===id).price*q,0); $('#cartTotal').textContent=money(total);
  $('#cartItems').querySelectorAll('[data-minus]').forEach(b=>b.addEventListener('click',()=>changeQty(Number(b.dataset.minus),-1)));
  $('#cartItems').querySelectorAll('[data-plus]').forEach(b=>b.addEventListener('click',()=>changeQty(Number(b.dataset.plus),1)));
}

function renderInventory(){
  $('#inventoryBody').innerHTML=state.products.map(p=>`<tr><td>${p.sku}</td><td class="table-product">${p.name}</td><td>${p.category}</td><td><input class="inline-input" id="price-${p.id}" type="number" min="0" step="1" value="${p.price}"></td><td><input class="inline-input stock" id="stock-${p.id}" type="number" min="0" step="1" value="${p.stock}"></td><td><span class="status-pill ${p.stock<=15?'low':''}">● ${p.stock<=15?'STOCK BAJO':'DISPONIBLE'}</span></td><td><button class="save-row" data-save="${p.id}">Guardar</button></td></tr>`).join('');
  $('#inventoryBody').querySelectorAll('[data-save]').forEach(b=>b.addEventListener('click',()=>saveInventory(Number(b.dataset.save))));
}
async function saveInventory(id){
  try{await api(`/api/products/${id}`,{method:'PATCH',body:JSON.stringify({price:Number($(`#price-${id}`).value),stock:Number($(`#stock-${id}`).value)})});await loadAll();toast('Inventario actualizado en SQLite.')}catch(e){toast(e.message,true)}
}

function renderSales(sales){
  $('#salesList').innerHTML=sales.length?sales.slice(0,6).map(s=>`<article class="sale-card"><small>VENTA #${String(s.id).padStart(3,'0')} · ${new Date(s.created_at).toLocaleString('es-MX')}</small><strong>${s.customer_name}</strong><span>${money(s.total)}</span></article>`).join(''):'<p class="empty-sale">Aún no hay ventas registradas. Haz una compra desde el carrito para crear la primera.</p>';
}

async function checkout(){
  if(!state.cart.size){toast('El carrito está vacío.',true);return}
  const items=[...state.cart.entries()].map(([product_id,quantity])=>({product_id,quantity}));
  try{const sale=await api('/api/sales',{method:'POST',body:JSON.stringify({customer_name:$('#customerName').value||'Cliente demo',items})});state.cart.clear();closeCart();await loadAll();toast(`Venta #${sale.id} registrada por ${money(sale.total)}`)}catch(e){toast(e.message,true)}
}

async function runAgent(e){
  e.preventDefault(); const output=$('#agentOutput');output.innerHTML='<div class="empty-state"><span class="pulse-core">···</span><strong>Agentes analizando</strong><p>Mercado → Catálogo → Inventario → Ventas → Calidad</p></div>';
  try{
    const result=await api('/api/agent/recommend',{method:'POST',body:JSON.stringify({profile:$('#profile').value,need:$('#need').value,budget:Number($('#budget').value)})});
    output.innerHTML=`<div class="agent-flow">${result.agents.map(a=>`<div class="agent-step"><b>${a.name}</b><span>${a.message}</span></div>`).join('')}</div><div class="agent-rec-title"><strong>Selección final</strong><span class="quality-ok">✓ A6 VALIDADO</span></div><div class="rec-grid">${result.recommendations.length?result.recommendations.map(r=>`<article class="rec-item"><small>${r.sku} · ${r.category}</small><strong>${r.name}</strong><span>${money(r.price)}</span><p>${r.reason}</p></article>`).join(''):'<p class="empty-sale">No hay opciones dentro del presupuesto actual.</p>'}</div>`;
  }catch(err){output.innerHTML=`<div class="empty-state"><strong>No se pudo completar</strong><p>${err.message}</p></div>`}
}

function openCart(){ $('#cartDrawer').classList.add('open');$('#scrim').classList.add('open');$('#cartDrawer').setAttribute('aria-hidden','false') }
function closeCart(){ $('#cartDrawer').classList.remove('open');$('#scrim').classList.remove('open');$('#cartDrawer').setAttribute('aria-hidden','true') }

$('#searchInput').addEventListener('input',e=>{state.search=e.target.value.trim().toLowerCase();renderProducts()});
$('#openCart').addEventListener('click',openCart);$('#closeCart').addEventListener('click',closeCart);$('#scrim').addEventListener('click',closeCart);$('#checkoutBtn').addEventListener('click',checkout);$('#agentForm').addEventListener('submit',runAgent);
loadAll().catch(e=>toast(e.message,true));
