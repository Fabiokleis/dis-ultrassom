let allData = [];
let selectedCard = null;

// Carrega relatório ao iniciar
window.addEventListener('DOMContentLoaded', loadReport);

async function loadReport() {
    try {
        const response = await fetch('/report/data');
        const data = await response.json();
        
        allData = data.reconstructions;
        renderCards(allData);
        
    } catch (error) {
        console.error('Erro ao carregar relatório:', error);
        document.getElementById('imageGrid').innerHTML = 
            '<div style="text-align: center; color: red;">❌ Erro ao carregar dados</div>';
    }
}

function renderCards(reconstructions) {
    const grid = document.getElementById('imageGrid');
    grid.innerHTML = '';
    
    reconstructions.forEach(item => {
        const card = createCard(item);
        grid.appendChild(card);
    });
}

function createCard(item) {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.jobId = item.job_id;
    
    const algorithmName = item.algorithm === 1 ? 'CGNE' : 'CGNR';
    
    card.innerHTML = `
        <img src="/imagens/${item.image_filename}" 
             alt="Job ${item.job_id}"
             loading="lazy">
        <div class="card-info">
            ${algorithmName}
        </div>
    `;
    
    card.addEventListener('click', () => showDetails(item, card));
    
    return card;
}

function showDetails(item, card) {
    // Remove seleção anterior
    if (selectedCard) {
        selectedCard.classList.remove('selected');
    }
    
    // Marca nova seleção
    card.classList.add('selected');
    selectedCard = card;
    
    const algorithmName = item.algorithm === 1 ? 'CGNE' : 'CGNR';
    const gainLabel = item.gain ? 'Sim' : 'Não';
    
    const sidebarContent = document.getElementById('sidebarContent');
    sidebarContent.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Job ID:</span>
            <span class="detail-value">${item.job_id}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Signal ID:</span>
            <span class="detail-value">${item.signal_id}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Scale:</span>
            <span class="detail-value">${item.scale}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Algoritmo:</span>
            <span class="detail-value">${algorithmName}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Ganho:</span>
            <span class="detail-value">${gainLabel}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Iterações:</span>
            <span class="detail-value">${item.iterations}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Duração:</span>
            <span class="detail-value">${item.duration_s.toFixed(3)}s</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Workers:</span>
            <span class="detail-value">${item.num_workers}</span>
        </div>
        
        <div class="detail-row">
            <span class="detail-label">Imagem:</span>
            <span class="detail-value" style="font-size: 10px; word-break: break-all;">${item.image_filename}</span>
        </div>
    `;
}
