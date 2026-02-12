const { createApp, ref, computed, onMounted, watch } = Vue;

createApp({
    setup() {
        const currentView = ref('dashboard');
        const isRefreshing = ref(false);
        const lastUpdated = ref(new Date().toLocaleTimeString());

        // State from LocalStorage
        const accounts = ref(JSON.parse(localStorage.getItem('accounts')) || [
            { name: 'Chase Checking', type: 'checking', balance: 5240.50 },
            { name: 'Marcus Savings', type: 'savings', balance: 12500.00 },
            { name: 'Vanguard Brokerage', type: 'investment', balance: 35000.00 },
            { name: 'Amex Gold', type: 'credit', balance: -450.20 }
        ]);
        const cryptoWallets = ref(JSON.parse(localStorage.getItem('cryptoWallets')) || [
            { name: 'Bitcoin', symbol: 'BTC', coinId: 'bitcoin', amount: 0.25 },
            { name: 'Ethereum', symbol: 'ETH', coinId: 'ethereum', amount: 2.5 }
        ]);
        const budgetLimits = ref(JSON.parse(localStorage.getItem('budgetLimits')) || {
            'Housing': 1500,
            'Food': 500,
            'Transport': 300,
            'Entertainment': 200,
            'Utilities': 150
        });
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const transactions = ref(JSON.parse(localStorage.getItem('transactions')) || [
            { id: 1, date: `${year}-${month}-05`, description: 'Safeway', category: 'Food', amount: -85.20 },
            { id: 2, date: `${year}-${month}-04`, description: 'Shell Gas', category: 'Transport', amount: -55.00 },
            { id: 3, date: `${year}-${month}-02`, description: 'Rent Payment', category: 'Housing', amount: -1500.00 },
            { id: 4, date: `${year}-${month}-01`, description: 'Netflix', category: 'Entertainment', amount: -15.99 },
            { id: 5, date: `${year}-${month}-03`, description: 'Dividend Pay', category: 'Income', amount: 120.50 }
        ]);
        const settings = ref(JSON.parse(localStorage.getItem('settings')) || {
            plaidEnabled: false,
            plaidAccessToken: '',
            currency: 'USD',
            homeValue: 450000,
            homeAddress: ''
        });

        // Modals
        const showAddAccountModal = ref(false);
        const showAddCryptoModal = ref(false);
        const showAddBudgetModal = ref(false);
        const showAddTransactionModal = ref(false);

        // Form inputs
        const newAccount = ref({ name: '', type: 'checking', balance: 0 });
        const newCrypto = ref({ name: '', symbol: '', coinId: '', amount: 0 });
        const newTx = ref({ description: '', amount: 0, date: new Date().toISOString().split('T')[0], category: 'Food' });
        const cryptoPrices = ref({});

        // Computed
        const totalCash = computed(() => {
            return accounts.value
                .filter(a => a.type === 'checking' || a.type === 'savings')
                .reduce((sum, a) => sum + parseFloat(a.balance), 0);
        });

        const totalInvestments = computed(() => {
            return accounts.value
                .filter(a => a.type === 'investment')
                .reduce((sum, a) => sum + parseFloat(a.balance), 0);
        });

        const totalCrypto = computed(() => {
            let total = 0;
            cryptoWallets.value.forEach(wallet => {
                const price = cryptoPrices.value[wallet.coinId]?.usd || 0;
                total += wallet.amount * price;
            });
            return total;
        });

        const netWorth = computed(() => {
            const accSum = accounts.value.reduce((sum, a) => sum + parseFloat(a.balance), 0);
            const home = parseFloat(settings.value.homeValue || 0);
            return accSum + totalCrypto.value + home;
        });

        const monthlySpending = computed(() => {
            const now = new Date();
            const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
            return transactions.value
                .filter(tx => new Date(tx.date) >= startOfMonth && tx.amount < 0)
                .reduce((sum, tx) => sum + Math.abs(tx.amount), 0);
        });

        const recentTransactions = computed(() => {
            return [...transactions.value].sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5);
        });

        // Watchers for persistence
        watch([accounts, cryptoWallets, budgetLimits, transactions, settings], () => {
            localStorage.setItem('accounts', JSON.stringify(accounts.value));
            localStorage.setItem('cryptoWallets', JSON.stringify(cryptoWallets.value));
            localStorage.setItem('budgetLimits', JSON.stringify(budgetLimits.value));
            localStorage.setItem('transactions', JSON.stringify(transactions.value));
            localStorage.setItem('settings', JSON.stringify(settings.value));
        }, { deep: true });

        // Methods
        const formatCurrency = (value) => {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: settings.value.currency,
            }).format(value);
        };

        const refreshData = async () => {
            isRefreshing.value = true;
            await fetchCryptoPrices();
            lastUpdated.value = new Date().toLocaleTimeString();
            setTimeout(() => {
                isRefreshing.value = false;
                initCharts();
            }, 500);
        };

        const fetchCryptoPrices = async () => {
            if (cryptoWallets.value.length === 0) return;
            const ids = cryptoWallets.value.map(w => w.coinId).join(',');
            try {
                const response = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd`);
                cryptoPrices.value = await response.json();
            } catch (error) {
                console.error('Crypto fetch error:', error);
            }
        };

        const addTransaction = () => {
            if (newTx.value.description && newTx.value.amount) {
                transactions.value.push({
                    ...newTx.value,
                    id: Date.now()
                });
                newTx.value = { description: '', amount: 0, date: new Date().toISOString().split('T')[0], category: 'Food' };
                showAddTransactionModal.value = false;
                initCharts();
            }
        };

        const addAccount = () => {
            if (newAccount.value.name) {
                accounts.value.push({ ...newAccount.value });
                newAccount.value = { name: '', type: 'checking', balance: 0 };
                showAddAccountModal.value = false;
            }
        };

        const removeAccount = (index) => {
            accounts.value.splice(index, 1);
        };

        const addCrypto = () => {
            if (newCrypto.value.coinId && newCrypto.value.amount) {
                const name = newCrypto.value.name || (newCrypto.value.coinId.charAt(0).toUpperCase() + newCrypto.value.coinId.slice(1));
                cryptoWallets.value.push({
                    ...newCrypto.value,
                    name,
                    symbol: newCrypto.value.symbol.toUpperCase()
                });
                newCrypto.value = { name: '', symbol: '', coinId: '', amount: 0 };
                showAddCryptoModal.value = false;
                fetchCryptoPrices();
            }
        };

        const removeCrypto = (index) => {
            cryptoWallets.value.splice(index, 1);
        };

        const getCategorySpending = (cat) => {
            return transactions.value
                .filter(tx => tx.category === cat && tx.amount < 0)
                .reduce((sum, tx) => sum + Math.abs(tx.amount), 0);
        };

        const getCategoryPercentage = (cat) => {
            const limit = budgetLimits.value[cat];
            if (!limit) return 0;
            return (getCategorySpending(cat) / limit) * 100;
        };

        const exportData = () => {
            const data = {
                accounts: accounts.value,
                cryptoWallets: cryptoWallets.value,
                budgetLimits: budgetLimits.value,
                transactions: transactions.value,
                settings: settings.value
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'finance-data-export.json';
            a.click();
        };

        const clearAllData = () => {
            if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
                localStorage.clear();
                location.reload();
            }
        };

        // Charts
        let spendingChart = null;
        let netWorthChart = null;
        let comparisonChart = null;

        const initCharts = () => {
            if (spendingChart) spendingChart.destroy();
            if (netWorthChart) netWorthChart.destroy();
            if (comparisonChart) comparisonChart.destroy();

            const spendingCtx = document.getElementById('spendingChart');
            if (spendingCtx) {
                const categories = Object.keys(budgetLimits.value);
                const data = categories.map(cat => getCategorySpending(cat));
                spendingChart = new Chart(spendingCtx, {
                    type: 'doughnut',
                    data: {
                        labels: categories,
                        datasets: [{
                            data: data,
                            backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
                        }]
                    },
                    options: { maintainAspectRatio: false }
                });
            }

            const netWorthCtx = document.getElementById('netWorthChart');
            if (netWorthCtx) {
                const months = [];
                const now = new Date();
                for (let i = 5; i >= 0; i--) {
                    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
                    months.push(d.toLocaleString('default', { month: 'short' }));
                }

                netWorthChart = new Chart(netWorthCtx, {
                    type: 'line',
                    data: {
                        labels: months,
                        datasets: [{
                            label: 'Net Worth',
                            data: [netWorth.value * 0.92, netWorth.value * 0.94, netWorth.value * 0.93, netWorth.value * 0.96, netWorth.value * 0.98, netWorth.value],
                            borderColor: '#4f46e5',
                            backgroundColor: 'rgba(79, 70, 229, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: false
                            }
                        }
                    }
                });
            }

            const compCtx = document.getElementById('budgetComparisonChart');
            if (compCtx && currentView.value === 'budget') {
                comparisonChart = new Chart(compCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Housing', 'Food', 'Transport', 'Entertainment'],
                        datasets: [
                            { label: 'Last Month', data: [1500, 480, 320, 250], backgroundColor: '#e2e8f0' },
                            { label: 'This Month', data: [1500, 450, 300, 200], backgroundColor: '#4f46e5' }
                        ]
                    },
                    options: { maintainAspectRatio: false }
                });
            }
        };

        const initPlaidLink = () => {
            alert('Plaid Link requires a backend to exchange tokens. In this personal dashboard, you can manually add accounts or use a local proxy.');
        };

        const lookupZillow = () => {
            if (!settings.value.homeAddress) {
                alert('Please enter an address first.');
                return;
            }
            alert('Zillow API lookup requires a backend or API key. Mocking value...');
            settings.value.homeValue = 450000 + Math.floor(Math.random() * 50000);
        };

        onMounted(() => {
            fetchCryptoPrices().then(() => {
                initCharts();
            });
        });

        watch(currentView, () => {
            setTimeout(initCharts, 0);
        });

        return {
            currentView, isRefreshing, lastUpdated,
            accounts, cryptoWallets, budgetLimits, transactions, settings,
            showAddAccountModal, showAddCryptoModal, showAddBudgetModal, showAddTransactionModal,
            newAccount, newCrypto, newTx, cryptoPrices,
            totalCash, totalInvestments, totalCrypto, netWorth, monthlySpending, recentTransactions,
            formatCurrency, refreshData, addAccount, removeAccount, addCrypto, removeCrypto,
            getCategorySpending, getCategoryPercentage, exportData, clearAllData, initPlaidLink, addTransaction, lookupZillow
        };
    }
}).mount('#app');
