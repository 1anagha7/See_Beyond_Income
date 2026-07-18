const API_BASE_URL = 'http://127.0.0.1:8000';

let mockTransactions = [];
let generatedQuest = null;
let currentRole = 'Customer'; // 'Customer' or 'BankAdmin'
let charts = {}; // Track Chart.js instances to destroy them before re-render
let simulatedDay = 1;

// DOM Elements - Login / Screens
const loginScreen = document.getElementById('login-screen');
const appContainer = document.getElementById('app-container');
const roleBadge = document.getElementById('role-badge');
const btnLoginCustomer = document.getElementById('btn-login-customer');
const btnLoginBank = document.getElementById('btn-login-bank');
const btnLogout = document.getElementById('btn-logout');

// Navigation Tabs
const customerNav = document.getElementById('customer-nav');
const bankNav = document.getElementById('bank-nav');
const customerPortal = document.getElementById('customer-portal');
const bankPortal = document.getElementById('bank-portal');

// Customer Profile Bar Elements
const profileName = document.getElementById('profile-name');
const profileLevel = document.getElementById('profile-level');
const profileXpText = document.getElementById('profile-xp-text');
const profileXpFill = document.getElementById('profile-xp-fill');
const profileStreak = document.getElementById('profile-streak');
const profileSavings = document.getElementById('profile-savings');

// Quest & Progress Elements
const tbody = document.querySelector('#transactions-table tbody');
const addRowBtn = document.getElementById('add-row-btn');
const generateQuestBtn = document.getElementById('generate-quest-btn');
const loader = document.getElementById('loader');
const loaderText = document.getElementById('loader-text');
const idleCard = document.getElementById('idle-card');
const questCard = document.getElementById('quest-card');
const questStatusBadge = document.getElementById('quest-status-badge');
const questCategoryTitle = document.getElementById('quest-category-title');
const questAnalysis = document.getElementById('quest-analysis');
const questTarget = document.getElementById('quest-target');
const questReduction = document.getElementById('quest-reduction');
const questDuration = document.getElementById('quest-duration');
const questRewardName = document.getElementById('quest-reward-name');
const completeQuestBtn = document.getElementById('complete-quest-btn');

// Progress Simulation inputs
const simDayVal = document.getElementById('sim-day-val');
const simSpendInput = document.getElementById('sim-spend-input');
const btnDayDown = document.getElementById('btn-day-down');
const btnDayUp = document.getElementById('btn-day-up');
const btnCheckProgress = document.getElementById('btn-check-progress');

// Recovery Box Elements
const recoveryQuestContainer = document.getElementById('recovery-quest-container');
const recoverySummary = document.getElementById('recovery-summary');
const recoveryQuestDescription = document.getElementById('recovery-quest-description');

// Unlock / Learning Card Elements
const unlockScreen = document.getElementById('unlock-screen');
const unlockedProductTitle = document.getElementById('unlocked-product-title');
const unlockLearningBtn = document.getElementById('unlock-learning-btn');
const learningCard = document.getElementById('learning-card');
const learnProductName = document.getElementById('learn-product-name');
const learnProductSubtitle = document.getElementById('learn-product-subtitle');
const learnExplainer = document.getElementById('learn-explainer');
const learnBenefitsList = document.getElementById('learn-benefits-list');
const investNowBtn = document.getElementById('invest-now-btn');
const resetFlowBtn = document.getElementById('reset-flow-btn');

// WhatsApp elements
const whatsappChatBody = document.getElementById('whatsapp-chat-body');
const btnClearChat = document.getElementById('btn-clear-chat');

// Bank KPIs
const bankKpiCustomers = document.getElementById('bank-kpi-customers');
const bankKpiSuccessRate = document.getElementById('bank-kpi-success-rate');
const bankKpiSavings = document.getElementById('bank-kpi-savings');
const bankKpiCommission = document.getElementById('bank-kpi-commission');
const bankCustomersTableBody = document.querySelector('#bank-customers-table tbody');

// Quick Action Buttons on Dashboard
const quickActionQuest = document.getElementById('quick-action-quest');
const quickActionWhatsapp = document.getElementById('quick-action-whatsapp');

// -------------------------------------------------------
// ROUTING & LOGIN LOGIC
// -------------------------------------------------------

btnLoginCustomer.addEventListener('click', () => {
    enterPortal('Customer');
});

btnLoginBank.addEventListener('click', () => {
    enterPortal('BankAdmin');
});

btnLogout.addEventListener('click', () => {
    appContainer.classList.add('hidden');
    loginScreen.classList.remove('hidden');
    loginScreen.classList.add('visible');
});

function enterPortal(role) {
    currentRole = role;
    roleBadge.innerText = role === 'Customer' ? 'Customer' : 'Bank Admin';
    roleBadge.className = `role-badge ${role === 'Customer' ? 'customer-badge' : 'bank-badge'}`;

    loginScreen.classList.remove('visible');
    loginScreen.classList.add('hidden');
    appContainer.classList.remove('hidden');
    appContainer.classList.add('visible');

    if (role === 'Customer') {
        customerNav.classList.remove('hidden');
        bankNav.classList.add('hidden');
        customerPortal.classList.remove('hidden');
        bankPortal.classList.add('hidden');
        switchTab('cust-dashboard');
        
        // Load initial customer details
        initCustomerData();
    } else {
        customerNav.classList.add('hidden');
        bankNav.classList.remove('hidden');
        customerPortal.classList.add('hidden');
        bankPortal.classList.remove('hidden');
        switchTab('bank-dashboard');
        
        // Load initial bank analytics
        initBankData();
    }
}

// Tab Switching
document.querySelectorAll('.nav-tab').forEach(tabButton => {
    tabButton.addEventListener('click', () => {
        const targetTab = tabButton.getAttribute('data-tab');
        switchTab(targetTab);
    });
});

function switchTab(tabId) {
    // 1. Update nav buttons state
    document.querySelectorAll('.nav-tab').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // 2. Hide all tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // 3. Show requested tab panel
    const targetPanel = document.getElementById(tabId);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
    
    // 4. Trigger specific fetches on tab load
    if (tabId === 'cust-dashboard') {
        renderDashboardActiveQuest();
        fetchWhatsAppNotifications();
    } else if (tabId === 'cust-whatsapp') {
        fetchWhatsAppNotifications();
    } else if (tabId === 'cust-yono') {
        renderYonoProductGateway();
    } else if (tabId === 'bank-dashboard') {
        fetchBankAnalytics();
    } else if (tabId === 'bank-customers') {
        fetchBankCustomers();
    }
}

// Connect quick actions
if (quickActionQuest) quickActionQuest.addEventListener('click', () => switchTab('cust-quest'));
if (quickActionWhatsapp) quickActionWhatsapp.addEventListener('click', () => switchTab('cust-whatsapp'));

// -------------------------------------------------------
// MOCK TRANSACTION TABLE LOGIC
// -------------------------------------------------------

function renderTable() {
    tbody.innerHTML = '';
    mockTransactions.forEach((tx, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="date" value="${tx.date}" onchange="updateTxField(${index}, 'date', this.value)"></td>
            <td><input type="text" value="${tx.category}" onchange="updateTxField(${index}, 'category', this.value)"></td>
            <td><input type="text" value="${tx.description}" onchange="updateTxField(${index}, 'description', this.value)"></td>
            <td><input type="number" value="${tx.amount}" onchange="updateTxField(${index}, 'amount', parseFloat(this.value))"></td>
            <td><button class="delete-btn" onclick="deleteTx(${index})">🗑️</button></td>
        `;
        tbody.appendChild(row);
    });
}

window.updateTxField = async function(index, field, value) {
    mockTransactions[index][field] = value;
    await syncTransactions();
};

window.deleteTx = async function(index) {
    mockTransactions.splice(index, 1);
    renderTable();
    await syncTransactions();
};

addRowBtn.addEventListener('click', async () => {
    const today = new Date().toISOString().split('T')[0];
    mockTransactions.push({ date: today, category: 'General', description: 'New expense', amount: 0 });
    renderTable();
    await syncTransactions();
});

async function syncTransactions() {
    try {
        const response = await fetch(`${API_BASE_URL}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transactions: mockTransactions })
        });
        if (response.ok) {
            const data = await response.json();
            mockTransactions = data;
        }
    } catch (e) {
        console.error('Error syncing transactions:', e);
    }
}

// -------------------------------------------------------
// CUSTOMER PORTAL DATA & ACTIONS
// -------------------------------------------------------

async function initCustomerData() {
    await fetchUserProfile();
    await fetchTransactions();
    await fetchActiveQuest();
    await fetchWhatsAppNotifications();
}

async function fetchUserProfile() {
    try {
        const res = await fetch(`${API_BASE_URL}/user`);
        if (res.ok) {
            const user = await res.json();
            profileName.innerText = user.name;
            profileLevel.innerText = user.level;
            profileStreak.innerText = user.streak;
            profileSavings.innerText = parseFloat(user.total_savings).toLocaleString('en-IN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            
            // XP bar calculation (XP relative to level threshold of 1000)
            const relativeXp = user.xp % 1000;
            profileXpText.innerText = `${relativeXp} / 1000 XP (Total: ${user.xp})`;
            profileXpFill.style.style = `width: ${(relativeXp / 1000) * 100}%;`;
            profileXpFill.style.width = `${(relativeXp / 1000) * 100}%`;
        }
    } catch (e) {
        console.error('Error fetching user profile:', e);
    }
}

async function fetchTransactions() {
    try {
        const res = await fetch(`${API_BASE_URL}/transactions`);
        if (res.ok) {
            const data = await res.json();
            mockTransactions = data;
            renderTable();
        }
    } catch (e) {
        console.error('Error fetching transactions:', e);
    }
}

async function fetchActiveQuest() {
    try {
        const res = await fetch(`${API_BASE_URL}/quest/active`);
        if (res.ok) {
            const quest = await res.json();
            if (quest) {
                generatedQuest = quest;
                renderQuestCard(quest);
            } else {
                generatedQuest = null;
                showCustomerCard(idleCard);
            }
        }
    } catch (e) {
        console.error('Error fetching active quest:', e);
    }
}

function showCustomerCard(cardElement) {
    [idleCard, loader, questCard, unlockScreen, learningCard].forEach(c => {
        c.classList.add('hidden');
        c.classList.remove('visible');
    });
    cardElement.classList.remove('hidden');
    cardElement.classList.add('visible');
}

// Render Active Quest details
function renderQuestCard(quest) {
    questCategoryTitle.innerText = `🎯 ${quest.category} Quest`;
    questAnalysis.innerText = quest.analysis || "We noticed a high spend category and formulated a savings plan.";
    questTarget.innerText = `₹${parseFloat(quest.target).toLocaleString('en-IN')}`;
    questReduction.innerText = `${quest.reduction_percentage}% Off`;
    questDuration.innerText = `${quest.duration} Days`;
    questRewardName.innerText = quest.reward;
    
    // Set stepper max value based on duration
    simDayVal.innerText = quest.current_day || 1;
    simulatedDay = quest.current_day || 1;
    
    // Calculate and pre-fill spend for this category
    const categorySpend = mockTransactions
        .filter(t => t.category.toLowerCase() === quest.category.toLowerCase())
        .reduce((sum, t) => sum + t.amount, 0);
    simSpendInput.value = categorySpend || 0;

    // Check status
    const expectedSpendRate = (quest.target / quest.duration) * simulatedDay;
    const isBehind = categorySpend > expectedSpendRate;
    
    if (isBehind) {
        questStatusBadge.innerText = 'BEHIND';
        questStatusBadge.className = 'status-badge danger-bg';
    } else {
        questStatusBadge.innerText = 'ON TRACK';
        questStatusBadge.className = 'status-badge success-bg';
    }

    // Update simulation recovery quest card if active quest status in database has recovery
    // (We will dynamically check progress on render)
    if (quest.status === 'completed') {
        unlockedProductTitle.innerText = quest.reward;
        showCustomerCard(unlockScreen);
    } else {
        showCustomerCard(questCard);
    }
}

// Generate quest trigger
generateQuestBtn.addEventListener('click', async () => {
    showCustomerCard(loader);
    loaderText.innerText = 'Orchestrating Goal Agent with LangGraph...';

    // Synchronize transactions first
    await syncTransactions();

    try {
        const response = await fetch(`${API_BASE_URL}/generate-quest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transactions: mockTransactions })
        });

        if (!response.ok) {
            throw new Error('Quest generation failed');
        }

        const data = await response.json();
        generatedQuest = data;
        renderQuestCard(data);
        await fetchUserProfile(); // Refresh XP bar
    } catch (e) {
        console.error(e);
        alert('Failed to generate quest. Verify backend is running.');
        showCustomerCard(idleCard);
    }
});

// Check Progress Simulation
btnDayDown.addEventListener('click', () => {
    if (simulatedDay > 1) {
        simulatedDay--;
        simDayVal.innerText = simulatedDay;
    }
});

btnDayUp.addEventListener('click', () => {
    if (generatedQuest && simulatedDay < generatedQuest.duration) {
        simulatedDay++;
        simDayVal.innerText = simulatedDay;
    }
});

btnCheckProgress.addEventListener('click', async () => {
    if (!generatedQuest) return;
    
    showCustomerCard(loader);
    loaderText.innerText = 'Behavioral & Motivation loop executing in LangGraph...';

    const payload = {
        current_day: simulatedDay,
        current_spend: parseFloat(simSpendInput.value) || 0
    };

    try {
        const res = await fetch(`${API_BASE_URL}/check-progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Progress check failed');

        const result = await res.json();
        
        // Re-fetch quest and user details
        await fetchUserProfile();
        await fetchActiveQuest(); // Recalculates card
        await fetchWhatsAppNotifications();
        
        // Render result card and toggle recovery box
        showCustomerCard(questCard);
        
        const isBehind = result.progress.status === 'Behind';
        if (isBehind && result.recovery) {
            recoveryQuestContainer.classList.remove('hidden');
            recoverySummary.innerText = result.recovery.summary;
            recoveryQuestDescription.innerText = result.recovery.recovery_quest;
            questStatusBadge.innerText = 'BEHIND';
            questStatusBadge.className = 'status-badge danger-bg';
        } else {
            recoveryQuestContainer.classList.add('hidden');
            questStatusBadge.innerText = 'ON TRACK';
            questStatusBadge.className = 'status-badge success-bg';
        }
        
        alert(`Daily Check-In Completed!\nStatus: ${result.progress.status}\nStreak: ${result.gamification.new_streak} days\nXP Gained: +${result.gamification.xp_earned} XP`);
        
    } catch (e) {
        console.error(e);
        alert('Progress check failed.');
        showCustomerCard(questCard);
    }
});

// Complete Quest Simulation
completeQuestBtn.addEventListener('click', () => {
    if (!generatedQuest) return;
    
    unlockedProductTitle.innerText = generatedQuest.reward;
    showCustomerCard(unlockScreen);
});

// Learning Explainer compiler
unlockLearningBtn.addEventListener('click', async () => {
    if (!generatedQuest) return;
    
    showCustomerCard(loader);
    loaderText.innerText = `Learning Agent unlocking explainer for ${generatedQuest.reward}...`;

    try {
        const res = await fetch(`${API_BASE_URL}/generate-learning-card`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_name: generatedQuest.reward })
        });

        if (!res.ok) throw new Error('Explainer compilation failed');

        const card = await res.json();
        
        learnProductName.innerText = card.product_name;
        learnProductSubtitle.innerText = card.subtitle;
        learnExplainer.innerText = card.explainer;
        
        learnBenefitsList.innerHTML = '';
        card.benefits.forEach(benefit => {
            const li = document.createElement('li');
            li.innerText = benefit;
            learnBenefitsList.appendChild(li);
        });

        showCustomerCard(learningCard);
        await fetchUserProfile(); // Update XP for unlocking learning card
    } catch (e) {
        console.error(e);
        alert('Learning compiler failed.');
        showCustomerCard(unlockScreen);
    }
});

// Product deep link click
investNowBtn.addEventListener('click', async () => {
    if (!generatedQuest) return;
    
    try {
        const res = await fetch(`${API_BASE_URL}/adopt-product`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quest_id: generatedQuest.id })
        });
        
        if (res.ok) {
            alert(`🎉 Congratulations! You have successfully invested in ${generatedQuest.reward} via SBI YONO deep-link.\n+1,000 XP rewarded!`);
            // Reset flow
            generatedQuest = null;
            await fetchUserProfile();
            showCustomerCard(idleCard);
        }
    } catch (e) {
        console.error(e);
        alert('Adoption deep-link failed.');
    }
});

resetFlowBtn.addEventListener('click', async () => {
    generatedQuest = null;
    showCustomerCard(idleCard);
});

// -------------------------------------------------------
// WHATSAPP SIMULATOR LOGIC
// -------------------------------------------------------

async function fetchWhatsAppNotifications() {
    try {
        const res = await fetch(`${API_BASE_URL}/notifications`);
        if (res.ok) {
            const logs = await res.json();
            
            // Clear current list, keep first welcome message
            whatsappChatBody.innerHTML = `
                <div class="chat-date">TODAY</div>
                <div class="message received">
                    <div class="msg-content">Welcome to SBI See Beyond Income! I will send you smart, non-intrusive motivational nudges here based on your quest progress. Keep checking in!</div>
                    <div class="msg-time">10:00</div>
                </div>
            `;
            
            // Append from db logs (which are sorted descending, so reverse to display oldest to newest)
            logs.reverse().forEach(log => {
                const dateObj = new Date(log.timestamp);
                const timeStr = dateObj.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
                
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message received';
                msgDiv.innerHTML = `
                    <div class="msg-content">${log.message}</div>
                    <div class="msg-time">${timeStr}</div>
                `;
                whatsappChatBody.appendChild(msgDiv);
            });
            
            // Scroll to bottom
            whatsappChatBody.scrollTop = whatsappChatBody.scrollHeight;
        }
    } catch (e) {
        console.error('Error fetching notifications:', e);
    }
}

btnClearChat.addEventListener('click', async () => {
    // Clear chat log locally or via endpoint if needed.
    // For simplicity, we just clear simulator display.
    whatsappChatBody.innerHTML = `
        <div class="chat-date">TODAY</div>
        <div class="message received">
            <div class="msg-content">Chat cleared. Welcome to SBI See Beyond Income!</div>
            <div class="msg-time">Just Now</div>
        </div>
    `;
});

// -------------------------------------------------------
// CUSTOMER PORTAL TAB: YONO REWARDS GATEWAY LOCKS
// -------------------------------------------------------

function renderYonoProductGateway() {
    const products = {
        "SBI Mutual Fund SIP": "prod-sip",
        "SBI Savings Account Plus": "prod-savings",
        "SBI Recurring Deposit": "prod-rd",
        "SBI Life Insurance": "prod-insurance"
    };
    
    // Reset all products to locked
    Object.values(products).forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.className = 'product-item-card locked';
            el.querySelector('.lock-indicator').innerText = '🔒';
        }
    });
    
    // Unlock currently active quest reward product
    if (generatedQuest) {
        const activeProdId = products[generatedQuest.reward];
        const el = document.getElementById(activeProdId);
        if (el) {
            el.className = 'product-item-card unlocked pulse-glow';
            el.querySelector('.lock-indicator').innerText = '🔓 UNLOCKED';
        }
    }
}

// -------------------------------------------------------
// CUSTOMER DASHBOARD ACTIVE QUEST RENDER
// -------------------------------------------------------

function renderDashboardActiveQuest() {
    const dashContainer = document.getElementById('dash-active-quest-container');
    if (!generatedQuest) {
        dashContainer.innerHTML = `
            <div class="empty-quest-dash text-center">
                <p>No active savings quest.</p>
                <button onclick="switchTab('cust-quest')" class="btn primary-btn btn-sm" style="margin-top:0.5rem;">Create Quest</button>
            </div>
        `;
    } else {
        dashContainer.innerHTML = `
            <div class="active-quest-dash">
                <h4>🎯 ${generatedQuest.category} Challenge</h4>
                <p>Maintain spend below <strong>₹${parseFloat(generatedQuest.target).toLocaleString()}</strong> for <strong>${generatedQuest.duration} days</strong>.</p>
                <div class="dash-quest-kpis">
                    <div>
                        <span>Spend: ₹${parseFloat(generatedQuest.current_spend || 0).toLocaleString()}</span>
                    </div>
                    <div>
                        <span>Reward: <strong>${generatedQuest.reward}</strong></span>
                    </div>
                </div>
            </div>
        `;
    }
}

// -------------------------------------------------------
// BANK ADMIN PORTAL DATA & CHARTS
// -------------------------------------------------------

async function initBankData() {
    await fetchBankAnalytics();
    await fetchBankCustomers();
}

async function fetchBankAnalytics() {
    try {
        const res = await fetch(`${API_BASE_URL}/bank/metrics`);
        if (res.ok) {
            const data = await res.json();
            
            // Populate stats
            bankKpiCustomers.innerText = data.total_users;
            bankKpiSuccessRate.innerText = `${data.quest_success_rate}%`;
            bankKpiSavings.innerText = `₹${parseFloat(data.total_savings).toLocaleString('en-IN')}`;
            bankKpiCommission.innerText = `₹${parseFloat(data.total_commission).toLocaleString('en-IN')}`;
            
            // Draw Charts
            renderConversionChart(data.product_funnel);
            renderCategoryChart(data.category_distribution);
        }
    } catch (e) {
        console.error('Error fetching bank metrics:', e);
    }
}

async function fetchBankCustomers() {
    try {
        const res = await fetch(`${API_BASE_URL}/bank/customers`);
        if (res.ok) {
            const customers = await res.json();
            bankCustomersTableBody.innerHTML = '';
            
            customers.forEach(c => {
                const tr = document.createElement('tr');
                
                const qName = c.active_quest ? `${c.active_quest.category} (${c.active_quest.reward})` : 'None';
                const qStatus = c.active_quest ? c.active_quest.status.toUpperCase() : 'INACTIVE';
                const nudge = c.last_notification ? c.last_notification.message : 'No nudges sent';
                
                let badgeClass = 'status-badge';
                if (qStatus === 'ACTIVE') badgeClass += ' success-bg';
                else if (qStatus === 'COMPLETED') badgeClass += ' success-bg';
                else if (qStatus === 'FAILED') badgeClass += ' danger-bg';
                else badgeClass += ' inactive-bg';
                
                tr.innerHTML = `
                    <td><strong>${c.name}</strong></td>
                    <td>Level ${c.level}</td>
                    <td>🔥 ${c.streak}</td>
                    <td>${c.xp} XP</td>
                    <td>${qName}</td>
                    <td><span class="${badgeClass}">${qStatus}</span></td>
                    <td class="table-nudge-text" title="${nudge}">${nudge}</td>
                    <td>₹${parseFloat(c.total_savings).toLocaleString('en-IN')}</td>
                `;
                bankCustomersTableBody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error('Error fetching customers directory:', e);
    }
}

function renderConversionChart(funnelData) {
    if (charts.conversion) charts.conversion.destroy();
    
    const ctx = document.getElementById('chart-product-conversion').getContext('2d');
    
    const products = funnelData.map(item => item.product);
    const recommended = funnelData.map(item => item.recommended);
    const unlocked = funnelData.map(item => item.unlocked);
    const adopted = funnelData.map(item => item.adopted);
    
    charts.conversion = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: products,
            datasets: [
                {
                    label: 'Quests Recommended',
                    data: recommended,
                    backgroundColor: 'rgba(255, 255, 255, 0.08)',
                    borderColor: 'rgba(255, 255, 255, 0.15)',
                    borderWidth: 1
                },
                {
                    label: 'Explainers Unlocked',
                    data: unlocked,
                    backgroundColor: 'rgba(0, 210, 255, 0.35)',
                    borderColor: '#00d2ff',
                    borderWidth: 1
                },
                {
                    label: 'Product Click & Adopt',
                    data: adopted,
                    backgroundColor: 'rgba(16, 185, 129, 0.45)',
                    borderColor: '#10b981',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: '#9ca3af', font: { family: 'Outfit', size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.03)' }
                },
                y: {
                    ticks: { color: '#9ca3af', font: { family: 'Outfit' } },
                    grid: { color: 'rgba(255, 255, 255, 0.03)' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#e5e7eb', font: { family: 'Outfit', size: 11 } }
                }
            }
        }
    });
}

function renderCategoryChart(distribution) {
    if (charts.categories) charts.categories.destroy();
    
    const ctx = document.getElementById('chart-quest-categories').getContext('2d');
    
    const labels = Object.keys(distribution);
    const data = Object.values(distribution);
    
    charts.categories = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#0063e5', '#00d2ff', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
                borderColor: 'rgba(11, 15, 25, 0.8)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#e5e7eb', font: { family: 'Outfit', size: 11 } }
                }
            }
        }
    });
}
