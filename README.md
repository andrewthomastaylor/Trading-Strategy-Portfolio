# Personal Finance Dashboard

A streamlined, single-page application to track your net worth, spending, and crypto portfolio.

## 🚀 How to Use

### Basic Mode (Manual Entry)
1.  **Open** `index.html` in any modern web browser.
    - You can manually add accounts and transactions. Data is saved in your browser's `localStorage`.

### Pro Mode (Real Bank Connection via Plaid)
To connect real bank accounts, you need to run a small local backend:

1.  **Install dependencies**:
    ```bash
    pip install flask flask-cors plaid-python python-dotenv
    ```
2.  **Configure Plaid**:
    - Copy `.env.example` to `.env`.
    - Get your API keys from [Plaid Dashboard](https://dashboard.plaid.com) and add them to `.env`.
3.  **Start the server**:
    ```bash
    python server.py
    ```
4.  **Connect**: Open `index.html`, go to **Accounts**, click **Add Account**, and then **Connect with Plaid**.

## ✨ Key Features

-   **Dashboard Overview**: See your Net Worth, Cash, Investments, Home Value, and Monthly Spending at a glance.
-   **Account Management**: Manually add and remove bank accounts, credit cards, and investment accounts.
-   **Crypto Tracking**: Enter your crypto holdings (using CoinGecko IDs like `bitcoin`, `ethereum`) and see real-time price updates.
-   **Transaction Logging**: Manually add transactions to track your spending and see it reflected in the "Spending Analysis" chart.
-   **Budgeting**: Set monthly budget limits for different categories and track your progress.
-   **Data Persistence**: All your data is saved locally in your browser's `localStorage`. It stays on your machine and is never sent to a server.
-   **Data Export**: Use the "Export Data (JSON)" button in Settings to back up your data.

## 🛠 Tech Stack

-   **Vue.js 3**: Reactive state management.
-   **Tailwind CSS**: Modern, responsive styling.
-   **Chart.js**: Dynamic financial visualizations.
-   **CoinGecko API**: Real-time crypto market data.

## 🔒 Security & Privacy

Since this app runs entirely in your browser and uses `localStorage`, your financial data never leaves your computer. This makes it a private and secure way to track your finances without needing to trust a third-party service with your login credentials.
