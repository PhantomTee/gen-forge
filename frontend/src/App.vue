<script setup lang="ts">
import { ref } from 'vue';
import { Code2, Rocket, Share2, AlertTriangle } from 'lucide-vue-next';
import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS || "0xYOUR_NEW_ADDRESS_HERE";
const userAddress = ref("");
const statusMessage = ref("System online. Awaiting architect login...");
const prompt = ref("");
const generatedCode = ref("");
const isArchitecting = ref(false);
const genClient = ref<any>(null);

const toast = ref({
  visible: false,
  message: "",
  type: "error"
});

const showToast = (msg: string, type: "error" | "success" = "error") => {
  toast.value = { visible: true, message: msg, type: type };
  setTimeout(() => { toast.value.visible = false; }, 4000);
};

const connectWallet = async () => {
  const ethWindow = window as any;
  if (!ethWindow.ethereum) {
    statusMessage.value = "ERROR: No Web3 provider found.";
    showToast("System Error: No Web3 wallet detected.", "error");
    return;
  }

  try {
    statusMessage.value = "Pinging wallet extension...";
    const accounts = await ethWindow.ethereum.request({ method: 'eth_requestAccounts' });
    userAddress.value = accounts[0];

    // Initialize 100% real GenLayer client
    genClient.value = createClient({
      chain: studionet,
      account: userAddress.value as `0x${string}`,
    });

    await genClient.value.connect("studionet");
    statusMessage.value = "Access granted. Ready to forge.";
    showToast("Wallet connected successfully!", "success");
  } catch (e: any) {
    statusMessage.value = "Connection Rejected or Failed.";
    showToast(`Connection failed: ${e.message}`, "error");
  }
};

const architectContract = async () => {
  if (!prompt.value?.trim()) {
    showToast("Please enter a prompt before generating", "error");
    return;
  }
  if (!genClient.value) {
    showToast("Please login first", "error");
    return;
  }

  isArchitecting.value = true;
  statusMessage.value = "ABI Encoding prompt and requesting signature...";

  try {
    // 1. Send the REAL Write Transaction via GenLayer SDK
    const txHash = await genClient.value.writeContract({
      address: contractAddress as `0x${string}`,
      functionName: 'draft_contract',
      args: [prompt.value],
      value: BigInt(0),
    });

    statusMessage.value = `Transaction sent! Hash: ${txHash}`;
    showToast("Transaction submitted to GenLayer", "success");
    statusMessage.value = "Waiting for GenVM Validators consensus...";

    // 2. Poll the network for real cryptographic finality
    await genClient.value.waitForTransactionReceipt({
      hash: txHash,
      status: 'FINALIZED',
    });

    statusMessage.value = "Consensus reached. Fetching generated code...";

    // 3. Read the actual AI-generated state from the blockchain
    const fetchedCode = await genClient.value.readContract({
      address: contractAddress as `0x${string}`,
      functionName: 'get_code',
      args: [prompt.value],
    });

    generatedCode.value = fetchedCode as string;
    statusMessage.value = "Intelligent Contract fetched successfully!";
    showToast("Architecture Complete ✓", "success");

  } catch (e: any) {
    console.error("GenForge Error:", e);
    let errorMsg = "Transaction failed. Please try again.";

    if (e.message?.toLowerCase().includes("rejected")) {
      errorMsg = "You rejected the transaction in MetaMask.";
    } else {
      errorMsg = `Execution failed: ${e.message.substring(0, 50)}...`;
    }

    statusMessage.value = errorMsg;
    showToast(errorMsg, "error");
  } finally {
    isArchitecting.value = false;
  }
};

const copyToClipboard = () => {
  navigator.clipboard.writeText(generatedCode.value);
  statusMessage.value = "Code copied to clipboard!";
  showToast("Code copied to clipboard!", "success");
};
</script>

<template>
  <div class="terminal-container">
    
    <Transition name="slide-fade">
      <div v-if="toast.visible" class="toast-notification" :class="toast.type">
        {{ toast.message }}
      </div>
    </Transition>

    <header class="window-header">
      <div class="window-controls">
        <span class="dot close"></span>
        <span class="dot minimize"></span>
        <span class="dot expand"></span>
      </div>
      <div class="window-title">
        phantomx@THALHAT: ~/gen-forge
      </div>
      <div class="header-actions">
        <div v-if="userAddress" class="user-pill">
          CONNECTED: {{ userAddress.substring(0, 6) }}...
        </div>
        <button v-else @click="connectWallet" class="sudo-btn">
          sudo login
        </button>
      </div>
    </header>

    <main class="terminal-body">
      
      <div class="ai-warning">
        <AlertTriangle :size="18" />
        <span>
          <strong>SYSTEM NOTICE:</strong> 
          AI-architected logic is susceptible to errors and hallucinations. 
          All generated Intelligent Contracts must be manually audited before deployment.
        </span>
      </div>

      <section class="pane">
        <div class="prompt-line">
          <span class="user">phantomx@THALHAT</span>:
          <span class="path">~/gen-forge</span>$ 
          <span class="cmd">architect --prompt</span>
        </div>
        
        <textarea 
          v-model="prompt" 
          placeholder="Describe the contract you want to build..."
          :disabled="isArchitecting"
          class="ubuntu-input"
        ></textarea>

        <button 
          @click="architectContract" 
          class="execute-btn"
          :disabled="isArchitecting || !userAddress"
        >
          <Rocket v-if="!isArchitecting" :size="18" />
          <span v-else class="loader"></span>
          {{ isArchitecting ? 'RUNNING CONSENSUS...' : 'EXECUTE' }}
        </button>
        
        <div class="logs">
          <p>> {{ statusMessage }}</p>
        </div>
      </section>

      <section class="pane output-bg">
        <div class="pane-header">
          <Code2 :size="16" />
          <span>/var/www/generated_contract.py</span>
          <button v-if="generatedCode" @click="copyToClipboard" class="copy-btn">
            <Share2 :size="14" />
          </button>
        </div>
        <div class="code-area">
          <div class="lines">
            <span v-for="n in 18" :key="n">{{ n }}</span>
          </div>
          <pre v-if="generatedCode">
            <code>{{ generatedCode }}</code>
          </pre>
          <div v-else class="cursor">_</div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
@import url('[https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@400;700&display=swap](https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@400;700&display=swap)');

.terminal-container {
  min-height: 100vh;
  background-color: #300a24;
  color: #fff;
  font-family: 'Ubuntu Mono', monospace;
  display: flex;
  flex-direction: column;
  padding: 15px;
}

/* AI Disclaimer Styles */
.ai-warning {
  grid-column: 1 / -1;
  background-color: rgba(223, 72, 20, 0.1);
  border: 1px solid #df4814;
  color: #ffb4a1;
  padding: 12px 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
}

.ai-warning strong {
  color: #df4814;
}

/* Base Terminal Styles */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 4px;
  color: white;
  font-weight: bold;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  border: 1px solid #ffffff33;
}
.toast-notification.error { background-color: #df4814; }
.toast-notification.success { background-color: #5eaa1a; }

.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.4s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to {
  transform: translateX(20px) translateY(-20px);
  opacity: 0;
}

.window-header {
  background-color: #4a4a4a;
  height: 35px;
  display: flex;
  align-items: center;
  padding: 0 15px;
  border-radius: 8px 8px 0 0;
  position: relative;
}
.window-controls { display: flex; gap: 8px; }
.dot { width: 12px; height: 12px; border-radius: 50%; }
.close { background: #df4814; }
.minimize { background: #efb73e; }
.expand { background: #5eaa1a; }

.window-title { 
  position: absolute; 
  left: 50%; 
  transform: translateX(-50%); 
  font-size: 0.85rem; 
  color: #ccc; 
}
.header-actions { margin-left: auto; }
.sudo-btn {
  background: #df4814;
  color: white;
  border: none;
  padding: 3px 12px;
  border-radius: 4px;
  font-family: inherit;
  cursor: pointer;
}

.terminal-body {
  flex: 1;
  background: rgba(48, 10, 36, 0.98);
  border: 1px solid #5e2750;
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 20px;
  gap: 20px;
}

.pane { display: flex; flex-direction: column; gap: 15px; }
.user { color: #87ff5f; font-weight: bold; }
.path { color: #5fafff; font-weight: bold; }
.cmd { color: #fff; margin-left: 8px; }

.ubuntu-input {
  flex: 1;
  background: rgba(0,0,0,0.2);
  border: 1px solid #5e2750;
  color: #38bdf8;
  padding: 15px;
  font-family: 'Ubuntu Mono', monospace;
  font-size: 1.1rem;
  resize: none;
  outline: none;
}

.execute-btn {
  background: #df4814;
  color: white;
  border: none;
  padding: 12px;
  font-family: inherit;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
}
.execute-btn:disabled { opacity: 0.5; }

.output-bg { 
  background: #1c1c1c; 
  border-radius: 4px; 
  border: 1px solid #333; 
}

.pane-header { 
  background: #333; 
  padding: 6px 15px; 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  font-size: 0.8rem; 
  color: #aaa; 
}
.copy-btn { margin-left: auto; background: none; border: none; color: #38bdf8; cursor: pointer; }

.code-area { display: flex; padding: 15px; font-size: 1rem; }
.lines { 
  display: flex; 
  flex-direction: column; 
  color: #555; 
  padding-right: 15px; 
  border-right: 1px solid #333; 
  text-align: right; 
}
pre { margin: 0; color: #f8f8f2; white-space: pre-wrap; }
.cursor { margin-left: 15px; animation: blink 1s infinite; color: #df4814; font-weight: bold; }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.loader { 
  width: 14px; 
  height: 14px; 
  border: 2px solid #fff; 
  border-top-color: transparent; 
  border-radius: 50%; 
  animation: spin 0.8s linear infinite; 
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) { .terminal-body { grid-template-columns: 1fr; } }
</style>