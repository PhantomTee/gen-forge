<script setup lang="ts">
import { ref } from 'vue';
import { Terminal, Code2, Rocket, Share2, Cpu } from 'lucide-vue-next';

/**
 * CONFIGURATION
 */
const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS || "PASTE_YOUR_ADDRESS_HERE";
const userAddress = ref("");
const statusMessage = ref("System Ready. Awaiting Connection...");

// State for the Forge
const prompt = ref("");
const generatedCode = ref("");
const isArchitecting = ref(false);

const targetNetwork = {
  chainId: '0x107d',
  chainName: 'GenLayer Asimov L2',
  rpcUrls: ['https://rpc.testnet-chain.genlayer.com'],
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 }
};

/**
 * WALLET LOGIC
 */
const connectWallet = async () => {
  const ethWindow = window as any;
  if (!ethWindow.ethereum) return;
  try {
    const accounts = await ethWindow.ethereum.request({ method: 'eth_requestAccounts' });
    userAddress.value = accounts[0];
    await ethWindow.ethereum.request({
      method: 'wallet_addEthereumChain',
      params: [targetNetwork],
    });
    statusMessage.value = "GenForge Core Online.";
  } catch (e) {
    statusMessage.value = "Connection Failed.";
  }
};

/**
 * GENFORGE LOGIC
 * This triggers the Intelligent Contract on Studionet
 */
const architectContract = async () => {
  if (!prompt.value) return;
  
  isArchitecting.value = true;
  statusMessage.value = "GenVM Validators reaching consensus on AI output...";
  
  try {
    const ethWindow = window as any;
    // Trigger real transaction to your GenForge contract
    const tx = await ethWindow.ethereum.request({
      method: 'eth_sendTransaction',
      params: [{
        from: userAddress.value,
        to: contractAddress,
        data: '0x', // In a full SDK, this encodes draft_contract(prompt.value)
      }]
    });

    console.log("TX Hash:", tx);
    
    // Simulation of the retrieval (In full build, you'd call get_code)
    setTimeout(() => {
      generatedCode.value = `from genlayer import *\n\nclass IntelligentContract:\n    def __init__(self):\n        self.owner = gl.message.sender\n\n    @gl.public.write\n    def execute_logic(self, val: int):\n        # Generated based on: ${prompt.value}\n        return f"Logic executed with {val}"`;
      statusMessage.value = "Contract Architected Successfully.";
      isArchitecting.value = false;
    }, 3000);

  } catch (e) {
    statusMessage.value = "Architecting Failed. Check Gas.";
    isArchitecting.value = false;
  }
};

const copyToClipboard = () => {
  navigator.clipboard.writeText(generatedCode.value);
  statusMessage.value = "Code copied to clipboard!";
};
</script>

<template>
  <div class="forge-app">
    <header class="header">
      <div class="brand">
        <Cpu class="icon-primary" />
        <h1>GEN<span>FORGE</span></h1>
      </div>
      <div v-if="userAddress" class="wallet-pill">
        {{ userAddress.substring(0, 6) }}...{{ userAddress.slice(-4) }}
      </div>
      <button v-else @click="connectWallet" class="connect-btn">Connect Architect</button>
    </header>

    <main class="forge-container">
      <section class="panel input-panel">
        <div class="panel-header">
          <Terminal :size="18" />
          <h2>Architect's Prompt</h2>
        </div>
        <div class="input-area">
          <textarea 
            v-model="prompt" 
            placeholder="Describe your contract... (e.g. 'A decentralized voting system for a DAO')"
            :disabled="isArchitecting"
          ></textarea>
          <button 
            @click="architectContract" 
            class="forge-btn"
            :disabled="isArchitecting || !userAddress"
          >
            <Rocket v-if="!isArchitecting" :size="20" />
            <div v-else class="loader"></div>
            {{ isArchitecting ? 'Architecting...' : 'Generate Intelligent Contract' }}
          </button>
        </div>
        <p class="status">{{ statusMessage }}</p>
      </section>

      <section class="panel output-panel">
        <div class="panel-header">
          <Code2 :size="18" />
          <h2>Generated Intelligent Logic (.py)</h2>
          <button @click="copyToClipboard" class="icon-btn" v-if="generatedCode">
            <Share2 :size="16" />
          </button>
        </div>
        <div class="code-viewer">
          <pre v-if="generatedCode"><code>{{ generatedCode }}</code></pre>
          <div v-else class="empty-state">
            <p>Awaiting architecture details...</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.forge-app {
  min-height: 100vh;
  background-color: #0f172a;
  color: #e2e8f0;
  font-family: 'Fira Code', monospace;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #1e293b;
  background: #0f172a;
}

.brand { display: flex; align-items: center; gap: 10px; }
.brand h1 { font-size: 1.5rem; font-weight: 800; letter-spacing: 2px; }
.brand span { color: #38bdf8; }
.icon-primary { color: #38bdf8; }

.wallet-pill {
  background: #1e293b;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.8rem;
  border: 1px solid #334155;
}

.connect-btn {
  background: #38bdf8;
  color: #0f172a;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.forge-container {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 40px;
}

.panel {
  background: #1e293b;
  border-radius: 12px;
  border: 1px solid #334155;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 15px 20px;
  background: #0f172a;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #334155;
}

.panel-header h2 { font-size: 0.9rem; font-weight: 600; text-transform: uppercase; flex: 1; }

.input-area { padding: 20px; flex: 1; display: flex; flex-direction: column; gap: 20px; }

textarea {
  flex: 1;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 20px;
  color: #38bdf8;
  font-family: inherit;
  resize: none;
  outline: none;
}

.forge-btn {
  background: #38bdf8;
  color: #0f172a;
  border: none;
  padding: 15px;
  border-radius: 8px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
}

.code-viewer {
  flex: 1;
  background: #020617;
  padding: 20px;
  overflow-y: auto;
  position: relative;
}

pre { margin: 0; color: #10b981; line-height: 1.6; font-size: 0.9rem; }

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
}

.status { padding: 10px 20px; font-size: 0.75rem; color: #94a3b8; font-style: italic; }

.loader {
  width: 20px;
  height: 20px;
  border: 3px solid #0f172a;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .forge-container { grid-template-columns: 1fr; }
}
</style>