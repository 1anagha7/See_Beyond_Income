const API_BASE_URL = 'http://127.0.0.1:8000';

let mockTransactions = [
    { date: '2026-07-10', category: 'Food & Dining', description: 'Zomato Order', amount: 850 },
    { date: '2026-07-11', category: 'Food & Dining', description: 'Dinner at Restaurant', amount: 2400 },
    { date: '2026-07-12', category: 'Shopping', description: 'Amazon Purchase', amount: 1200 },
    { date: '2026-07-13', category: 'Food & Dining', description: 'Swiggy Grocery', amount: 650 },
    { date: '2026-07-14', category: 'Transport', description: 'Uber Ride', amount: 300 },
    { date: '2026-07-15', category: 'Food & Dining', description: 'Starbucks Coffee', amount: 450 },
    { date: '2026-07-16', category: 'Utilities', description: 'Mobile Bill', amount: 799 }
];

let generatedQuest = null;

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
const questCategoryTitle = document.getElementById('quest-category-title');
const questAnalysis = document.getElementById('quest-analysis');
const questTarget = document.getElementById('quest-target');
const questReduction = document.getElementById('quest-reduction');
const questDuration = document.getElementById('quest-duration');
const questRewardName = document.getElementById('quest-reward-name');
const completeQuestBtn = document.getElementById('complete-quest-btn');

// Elements inside Unlock Screen
const unlockedProductTitle = document.getElementById('unlocked-product-title');
const unlockLearningBtn = document.getElementById('unlock-learning-btn');

// Elements inside Learning Card
const learnProductName = document.getElementById('learn-product-name');
const learnProductSubtitle = document.getElementById('learn-product-subtitle');
const learnExplainer = document.getElementById('learn-explainer');
const learnBenefitsList = document.getElementById('learn-benefits-list');
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

// Analyze transactions and call /generate-quest
generateQuestBtn.addEventListener('click', async () => {
    hideAllCards();
    showCard(loader);
    loaderText.innerText = 'Analyzing transactions & designing quest...';

    // Build payload
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
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to generate quest');
        }

        const data = await response.json();
        generatedQuest = data.quest;

        // Populate Quest Card
        questCategoryTitle.innerText = `🎯 ${data.top_category} Quest`;
        questAnalysis.innerText = data.analysis;
        questTarget.innerText = `₹${parseFloat(data.quest.target).toLocaleString()}`;
        questReduction.innerText = `${data.quest.reduction_percentage}% Off`;
        questDuration.innerText = `${data.quest.duration} Days`;
        questRewardName.innerText = data.quest.reward;

        hideAllCards();
        showCard(questCard);

    } catch (error) {
        console.error('Error generating quest:', error);
        alert('Could not connect to the backend server. Please verify it is running.');
        hideAllCards();
        showCard(idleCard);
    }
});

// Simulate quest completion
completeQuestBtn.addEventListener('click', () => {
    if (!generatedQuest) return;
    
    // Set up Product Unlock Screen
    unlockedProductTitle.innerText = generatedQuest.reward;

    hideAllCards();
    showCard(unlockScreen);
});

// Unlock learning gate & generate card
unlockLearningBtn.addEventListener('click', async () => {
    if (!generatedQuest) return;

    hideAllCards();
    showCard(loader);
    loaderText.innerText = `Unlocking learning gate & compiling product details for ${generatedQuest.reward}...`;

    try {
        const response = await fetch(`${API_BASE_URL}/generate-learning-card`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_name: generatedQuest.reward })
        });

        if (!response.ok) {
            throw new Error('Failed to generate learning card');
        }

        const data = await response.json();

        // Populate Learning Card
        learnProductName.innerText = data.product_name;
        learnProductSubtitle.innerText = data.subtitle;
        learnExplainer.innerText = data.explainer;

        learnBenefitsList.innerHTML = '';
        data.benefits.forEach(benefit => {
            const li = document.createElement('li');
            li.innerText = benefit;
            learnBenefitsList.appendChild(li);
        });

        hideAllCards();
        showCard(learningCard);

    } catch (error) {
        console.error('Error generating learning card:', error);
        alert('Could not connect to the backend server to fetch the learning card.');
        hideAllCards();
        showCard(unlockScreen);
    }
});

investNowBtn.addEventListener('click', () => {
    alert(`Congratulations! You have initiated investment setup for ${generatedQuest ? generatedQuest.reward : 'your product'}.`);
});

resetFlowBtn.addEventListener('click', () => {
    generatedQuest = null;
    hideAllCards();
    showCard(idleCard);
});

// Initialize
renderTable();
