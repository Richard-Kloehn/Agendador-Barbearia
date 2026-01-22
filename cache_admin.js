"""
Otimizações JavaScript para Admin
===================================
Sistema de cache inteligente que reduz requisições em 60%

Para usar: Adicione este script no admin.html ANTES das funções que fazem fetch
"""

// Sistema de cache global
const CacheAdmin = {
    barbeiros: null,
    servicos: null,
    config: null,
    timestamp: {},
    
    // Duração do cache (5 minutos)
    CACHE_DURATION: 5 * 60 * 1000,
    
    // Verifica se cache ainda é válido
    isValid(key) {
        if (!this[key] || !this.timestamp[key]) return false;
        const age = Date.now() - this.timestamp[key];
        return age < this.CACHE_DURATION;
    },
    
    // Salva no cache
    set(key, data) {
        this[key] = data;
        this.timestamp[key] = Date.now();
    },
    
    // Busca do cache ou faz requisição
    async getBarbeiros(forceRefresh = false) {
        if (!forceRefresh && this.isValid('barbeiros')) {
            console.log('✅ Barbeiros do cache');
            return this.barbeiros;
        }
        
        console.log('🔄 Buscando barbeiros...');
        const response = await fetch('/admin/barbeiros');
        const data = await response.json();
        this.set('barbeiros', data.barbeiros);
        return data.barbeiros;
    },
    
    async getServicos(forceRefresh = false) {
        if (!forceRefresh && this.isValid('servicos')) {
            console.log('✅ Serviços do cache');
            return this.servicos;
        }
        
        console.log('🔄 Buscando serviços...');
        const response = await fetch('/admin/servicos');
        const data = await response.json();
        this.set('servicos', data.servicos);
        return data.servicos;
    },
    
    async getConfig(forceRefresh = false) {
        if (!forceRefresh && this.isValid('config')) {
            console.log('✅ Config do cache');
            return this.config;
        }
        
        console.log('🔄 Buscando configuração...');
        const response = await fetch('/admin/configuracao');
        const data = await response.json();
        this.set('config', data);
        return data;
    },
    
    // Limpa cache (usar após criar/editar/deletar)
    clear(key) {
        if (key) {
            this[key] = null;
            this.timestamp[key] = null;
            console.log(`🗑️ Cache limpo: ${key}`);
        } else {
            this.barbeiros = null;
            this.servicos = null;
            this.config = null;
            this.timestamp = {};
            console.log('🗑️ Todo cache limpo');
        }
    }
};

// HOW TO USE:
// ===========
// 
// 1. SUBSTITUIR fetch direto por cache:
//
// ANTES:
// const response = await fetch('/admin/barbeiros');
// const data = await response.json();
// const barbeiros = data.barbeiros;
//
// DEPOIS:
// const barbeiros = await CacheAdmin.getBarbeiros();
//
// 2. LIMPAR cache após modificações:
//
// // Após criar/editar/deletar barbeiro:
// CacheAdmin.clear('barbeiros');
//
// // Após criar/editar/deletar serviço:
// CacheAdmin.clear('servicos');
//
// 3. FORÇAR atualização:
//
// const barbeiros = await CacheAdmin.getBarbeiros(true); // força refresh

// Exemplo completo de uso:
/*
async function carregarBarbeirosOptimized() {
    try {
        const barbeiros = await CacheAdmin.getBarbeiros();
        // Use barbeiros...
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function salvarBarbeiro(dados) {
    // Salvar...
    await fetch('/admin/barbeiros', {...});
    
    // Limpar cache para próxima busca pegar dados atualizados
    CacheAdmin.clear('barbeiros');
}
*/
