// ==================================================
// MELHORIAS DE UX - JavaScript
// ==================================================
// Adicionar ao <script> do index.html

// ========== CACHE DE HORÁRIOS ==========
const cacheHorarios = {
    data: {},
    ttl: 5 * 60 * 1000, // 5 minutos
    
    getKey(data, barbeiroId, servicoId) {
        return `${data}_${barbeiroId}_${servicoId}`;
    },
    
    get(data, barbeiroId, servicoId) {
        const key = this.getKey(data, barbeiroId, servicoId);
        const cached = this.data[key];
        
        if (cached && Date.now() - cached.timestamp < this.ttl) {
            console.log('✅ Usando horários em cache');
            return cached.horarios;
        }
        return null;
    },
    
    set(data, barbeiroId, servicoId, horarios) {
        const key = this.getKey(data, barbeiroId, servicoId);
        this.data[key] = {
            horarios: horarios,
            timestamp: Date.now()
        };
    },
    
    clear() {
        this.data = {};
    }
};

// ========== TOAST NOTIFICATIONS ==========
function showToast(message, type = 'info', duration = 4000) {
    // Remover toasts anteriores
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    // Criar novo toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        'success': '<i class="fas fa-check-circle text-2xl"></i>',
        'error': '<i class="fas fa-times-circle text-2xl"></i>',
        'warning': '<i class="fas fa-exclamation-triangle text-2xl"></i>',
        'info': '<i class="fas fa-info-circle text-2xl"></i>'
    };
    
    toast.innerHTML = `
        ${icon[type]}
        <span class="flex-1">${message}</span>
        <button onclick="this.parentElement.remove()" class="text-white hover:opacity-80">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remover após duração
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Substituir mostrarNotificacao por showToast
window.mostrarNotificacao = showToast;

// ========== SKELETON SCREENS ==========
function criarSkeletonBarbeiros() {
    return `
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-card"></div>
    `;
}

function criarSkeletonServicos() {
    return `
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-card"></div>
    `;
}

function criarSkeletonHorarios() {
    return `
        ${Array(12).fill('').map(() => `
            <div class="skeleton" style="height: 48px; border-radius: 8px;"></div>
        `).join('')}
    `;
}

// ========== VALIDAÇÃO TELEFONE EM TEMPO REAL ==========
function validarTelefoneReal(input) {
    const telefone = input.value.replace(/\D/g, '');
    const validationMsg = input.parentElement.querySelector('.validation-message') || document.createElement('div');
    
    if (!input.parentElement.querySelector('.validation-message')) {
        validationMsg.className = 'validation-message';
        input.parentElement.appendChild(validationMsg);
    }
    
    if (telefone.length === 0) {
        input.classList.remove('input-valid', 'input-invalid');
        validationMsg.innerHTML = '';
        return;
    }
    
    if (telefone.length >= 10 && telefone.length <= 11) {
        input.classList.add('input-valid');
        input.classList.remove('input-invalid');
        validationMsg.className = 'validation-message valid';
        validationMsg.innerHTML = '<i class="fas fa-check-circle"></i> Telefone válido';
    } else {
        input.classList.add('input-invalid');
        input.classList.remove('input-valid');
        validationMsg.className = 'validation-message invalid';
        validationMsg.innerHTML = '<i class="fas fa-times-circle"></i> Telefone incompleto';
    }
}

// ========== CARREGAR HORÁRIOS COM CACHE E SKELETON ==========
async function carregarHorariosComCache(data, barbeiroId, servicoId) {
    const container = document.getElementById('horariosContainer');
    const grid = document.getElementById('horariosGrid');
    
    // Verificar cache primeiro
    const cached = cacheHorarios.get(data, barbeiroId, servicoId);
    if (cached) {
        renderizarHorarios(cached);
        container.classList.remove('hidden');
        return;
    }
    
    // Mostrar skeleton
    container.classList.remove('hidden');
    grid.innerHTML = criarSkeletonHorarios();
    
    try {
        const response = await fetch(`/api/horarios-disponiveis?data=${data}&barbeiro_id=${barbeiroId}&servico_id=${servicoId}`);
        const dados = await response.json();
        
        if (dados.disponiveis && dados.disponiveis.length > 0) {
            cacheHorarios.set(data, barbeiroId, servicoId, dados.disponiveis);
            renderizarHorarios(dados.disponiveis);
        } else {
            grid.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-8">
                        <i class="fas fa-calendar-times text-6xl text-yellow-500 mb-4"></i>
                        <h3 class="text-xl font-bold text-gray-800 mb-2">Nenhum Horário Disponível</h3>
                        <p class="text-gray-600 mb-4">Não há horários livres para esta data.</p>
                        <button onclick="entrarListaEspera()" class="btn-primary text-white px-6 py-2 rounded-lg">
                            <i class="fas fa-bell mr-2"></i>Entrar na Lista de Espera
                        </button>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        showToast('Erro ao carregar horários. Tente novamente.', 'error');
        console.error(error);
    }
}

function renderizarHorarios(horarios) {
    const grid = document.getElementById('horariosGrid');
    grid.innerHTML = '';
    
    horarios.forEach(horario => {
        const button = document.createElement('button');
        button.className = 'horario-slot bg-white border-2 border-gray-200 rounded-lg py-3 px-2 hover:border-yellow-600 transition text-sm font-semibold text-gray-800';
        button.textContent = horario;
        button.onclick = () => selecionarHorario(horario, button);
        grid.appendChild(button);
    });
}

// ========== LISTA DE ESPERA ==========
async function entrarListaEspera() {
    const data = document.getElementById('data').value;
    const nome = dadosAgendamento.nome || document.getElementById('nome').value;
    const telefone = dadosAgendamento.telefone || document.getElementById('telefone').value;
    
    if (!nome || !telefone) {
        showToast('Por favor, preencha seus dados primeiro', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/lista-espera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome_cliente: nome,
                telefone: telefone,
                data_desejada: data,
                barbeiro_id: barbeiroSelecionado?.id,
                servico_id: servicoSelecionado?.id
            })
        });
        
        const resultado = await response.json();
        
        if (response.ok) {
            showToast('✅ Você entrou na lista de espera! Avisaremos quando houver vagas.', 'success', 5000);
        } else {
            showToast(resultado.erro || 'Erro ao entrar na lista de espera', 'error');
        }
    } catch (error) {
        showToast('Erro ao processar solicitação', 'error');
        console.error(error);
    }
}

// ========== INICIALIZAÇÃO ==========
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar validação em tempo real no telefone
    const telefoneInput = document.getElementById('telefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function(e) {
            // Máscara existente
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
                value = value.replace(/(\d)(\d{4})$/, '$1-$2');
                e.target.value = value;
            }
            
            // Validação em tempo real
            validarTelefoneReal(e.target);
        });
    }
    
    console.log('✅ Melhorias de UX carregadas');
});
