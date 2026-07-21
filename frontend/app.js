const API_BASE_URL = 'http://127.0.0.1:8000';

let mockTransactions = [
    { date: '2026-07-10', category: 'Food & Dining', description: 'Friday Night Restaurant', amount: 2400 },
    { date: '2026-07-11', category: 'Food & Dining', description: 'Zomato Weekend Delivery', amount: 850 },
    { date: '2026-07-11', category: 'Food & Dining', description: 'Saturday Cafe Outing', amount: 1100 },
    { date: '2026-07-12', category: 'Food & Dining', description: 'Sunday Swiggy Dinner', amount: 1850 },
    { date: '2026-07-13', category: 'Subscriptions', description: 'Netflix Monthly Sub', amount: 649 },
    { date: '2026-07-14', category: 'Shopping', description: 'Amazon Impulse Clothes', amount: 2200 },
    { date: '2026-07-15', category: 'Transport', description: 'Uber Office Ride', amount: 350 }
];

let currentQuestResult = null;

// DOM Elements
const tbody = document.querySelector('#transactions-table tbody');
const addRowBtn = document.getElementById('add-row-btn');
const generateQuestBtn = document.getElementById('generate-quest-btn');
const loader = document.getElementById('loader');
const loaderText = document.getElementById('loader-text');
const idleCard = document.getElementById('idle-card');
const questCard = document.getElementById('quest-card');
const unlockScreen = document.getElementById('unlock-screen');
const learningCard = document.getElementById('learning-card');

// Elements inside Quest Card
const questTitleText = document.getElementById('quest-title-text');
const statTotal = document.getElementById('stat-total');
const statTopCat = document.getElementById('stat-top-cat');
const statWeekendPct = document.getElementById('stat-weekend-pct');
const questWhyReasoning = document.getElementById('quest-why-reasoning');
const questTargetReduction = document.getElementById('quest-target-reduction');
const questDuration = document.getElementById('quest-duration');
const questReward = document.getElementById('quest-reward');
const completeQuestBtn = document.getElementById('complete-quest-btn');

// Elements inside Unlock Screen
const unlockLearningBtn = document.getElementById('unlock-learning-btn');

// Elements inside Learning Card
const learnTopicTitle = document.getElementById('learn-topic-title');
const learnSubtitle = document.getElementById('learn-subtitle');
const learnExplainer = document.getElementById('learn-explainer');
const learnTakeawaysList = document.getElementById('learn-takeaways-list');
const learnRecommendedAction = document.getElementById('learn-recommended-action');
const investNowBtn = document.getElementById('invest-now-btn');
const resetFlowBtn = document.getElementById('reset-flow-btn');

// Render transactions table
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

window.updateTxField = function(index, field, value) {
    mockTransactions[index][field] = value;
};

window.deleteTx = function(index) {
    mockTransactions.splice(index, 1);
    renderTable();
};

addRowBtn.addEventListener('click', () => {
    const today = new Date().toISOString().split('T')[0];
    mockTransactions.push({ date: today, category: 'General', description: 'New expense', amount: 0 });
    renderTable();
});

// Hide all display cards
function hideAllCards() {
    [idleCard, questCard, unlockScreen, learningCard, loader].forEach(card => {
        card.classList.add('hidden');
        card.classList.remove('visible');
    });
}

// Show specific display card
function showCard(card) {
    card.classList.remove('hidden');
    card.classList.add('visible');
}

// Run Analytics Engine & Generate Quest
generateQuestBtn.addEventListener('click', async () => {
    hideAllCards();
    showCard(loader);
    loaderText.innerText = 'Crunching deterministic analytics & generating mission...';

    const payload = {
        transactions: mockTransactions.map(tx => ({
            amount: parseFloat(tx.amount) || 0,
            category: tx.category || 'General',
            description: tx.description || '',
            date: tx.date || ''
        }))
    };

    try {
        const response = await fetch(`${API_BASE_URL}/generate-quest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to generate mission');
        }

        const data = await response.json();
        currentQuestResult = data;

        // Populate Quest Card with Deterministic Stats + Explainability Reasoning
        questTitleText.innerText = `🎯 ${data.quest_title || 'Financial Savings Mission'}`;
        
        if (data.analytics) {
            statTotal.innerText = `₹${parseFloat(data.analytics.total_spend).toLocaleString()}`;
            statTopCat.innerText = data.analytics.top_category;
            statWeekendPct.innerText = `${data.analytics.top_category_weekend_pct}%`;
        }

        questWhyReasoning.innerText = data.why_reasoning;
        questTargetReduction.innerText = `₹${parseFloat(data.target_reduction).toLocaleString()}`;
        questDuration.innerText = `${data.duration_days} Days`;
        questReward.innerText = data.reward_product;

        hideAllCards();
        showCard(questCard);

    } catch (error) {
        console.error('Error generating mission:', error);
        alert('Could not connect to FinPilot backend. Please ensure uvicorn is running.');
        hideAllCards();
        showCard(idleCard);
    }
});

// Simulate quest completion
completeQuestBtn.addEventListener('click', () => {
    if (!currentQuestResult) return;
    hideAllCards();
    showCard(unlockScreen);
});

// Launch Adaptive Micro-Lesson
unlockLearningBtn.addEventListener('click', async () => {
    if (!currentQuestResult) return;

    hideAllCards();
    showCard(loader);
    loaderText.innerText = 'Evaluating financial context & generating adaptive micro-lesson...';

    const learningPayload = {
        category: currentQuestResult.top_category || 'General',
        quest_title: currentQuestResult.quest_title || 'Savings Mission',
        struggle_context: currentQuestResult.why_reasoning || 'High discretionary spending'
    };

    try {
        const response = await fetch(`${API_BASE_URL}/generate-learning-card`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(learningPayload)
        });

        if (!response.ok) {
            throw new Error('Failed to generate adaptive micro-lesson');
        }

        const data = await response.json();

        // Populate Adaptive Learning Card
        learnTopicTitle.innerText = data.topic_title || 'Financial Mastery';
        learnSubtitle.innerText = data.subtitle || 'Smart Money Habits';
        learnExplainer.innerText = data.explainer_30s || '';

        learnTakeawaysList.innerHTML = '';
        if (data.key_takeaways) {
            data.key_takeaways.forEach(takeaway => {
                const li = document.createElement('li');
                li.innerText = takeaway;
                learnTakeawaysList.appendChild(li);
            });
        }

        learnRecommendedAction.innerText = data.recommended_action || 'Start building your financial discipline today.';

        hideAllCards();
        showCard(learningCard);

    } catch (error) {
        console.error('Error generating learning card:', error);
        alert('Could not fetch adaptive learning module from backend.');
        hideAllCards();
        showCard(unlockScreen);
    }
});

investNowBtn.addEventListener('click', () => {
    alert('Action executed! FinPilot is automating your savings workflow.');
});

resetFlowBtn.addEventListener('click', () => {
    currentQuestResult = null;
    hideAllCards();
    showCard(idleCard);
});

// Initialize table on load
renderTable();
