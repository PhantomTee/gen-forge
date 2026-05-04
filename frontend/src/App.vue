<script setup lang="ts">
import { ref, reactive } from 'vue'; // ADDED 'reactive' HERE
import { Code2, Rocket, Share2, AlertTriangle } from 'lucide-vue-next';
import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const userAddress = ref("");
const statusMessage = ref("System online. Awaiting architect login...");
const prompt = ref("");
const generatedCode = ref("");
const isArchitecting = ref(false);
const genClient = ref<any>(null);
const isLeaderOnly = ref(false);

const toast = ref({
  visible: false,
  message: "",
  type: "error"
});

// --- TAB & QUEUE STATE ---
const activeTab = ref('forge');
const tasks = ref<Array<{ id: number, prompt: string, status: string, code: string }>>([]);
let nextTaskId = 1;

// --- WALLET LOGIC ---
const disconnectWallet = () => {
  userAddress.value = '';
  genClient.value = null;
  statusMessage.value = "Wallet disconnected.";
  showToast("Wallet disconnected.", "success");
};

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

    genClient.value = createClient({
      chain: studionet,
      account: userAddress.value as `0x${string}`,
    });

    await genClient.value.connect("testnetAsimov");
    statusMessage.value = "Access granted. Ready to forge.";
    showToast("Wallet connected successfully!", "success");
  } catch (e: any) {
    statusMessage.value = "Connection Rejected or Failed.";
    showToast(`Connection failed: ${e.message}`, "error");
  }
};

// --- MULTI-TASK ARCHITECT LOGIC ---
const architectContract = async () => {
  if (!prompt.value || !userAddress.value) return;

  const currentPrompt = prompt.value;
  prompt.value = ""; 
  
  const taskId = nextTaskId++;
  const newTask = reactive({ id: taskId, prompt: currentPrompt, status: 'Initializing...', code: '' });
  tasks.value.unshift(newTask); 
  activeTab.value = 'tasks'; 

  try {
    newTask.status = 'Submitting to Asimov...';
    const txHash = await genClient.value.writeContract({
      address: import.meta.env.VITE_CONTRACT_ADDRESS as `0x${string}`,
      functionName: 'draft_contract',
      args: [currentPrompt],
      value: BigInt(0),
      leaderOnly: isLeaderOnly.value,
    });

    newTask.status = 'Waiting for AI Consensus (can take a few minutes)...';
    await genClient.value.waitForTransactionReceipt({
      hash: txHash,
      status: 'FINALIZED',
      interval: 5000,
      retries: 120,
    });

    newTask.status = 'Fetching Final Code...';
    const result = await genClient.value.readContract({
      address: import.meta.env.VITE_CONTRACT_ADDRESS as `0x${string}`,
      functionName: 'get_code',
      args: [currentPrompt],
    });

    newTask.status = 'Completed ✅';
    newTask.code = result as string;
    
    // Automatically show the code in the right pane if it finishes
    generatedCode.value = result as string;
    
  } catch (error: any) {
    console.error("Task failed:", error);
    newTask.status = `Failed ❌: ${error.message || 'Unknown Error'}`;
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
        user@root: ~/gen-forge
      </div>
      <div class="header-actions">
        <div v-if="userAddress" class="connected-group">
          <div class="user-pill">
            CONNECTED: {{ userAddress.substring(0, 6) }}...
          </div>
          <button @click="disconnectWallet" class="sudo-btn logout-btn">
            sudo logout
          </button>
        </div>
        <button v-else @click="connectWallet" class="sudo-btn">
          sudo login
        </button>
      </div>
    </header>

    <main class="terminal-body">
      
      <section class="pane">
        <div class="ai-warning">
          <AlertTriangle :size="18" />
          <span>
            <strong>SYSTEM NOTICE:</strong> 
            AI-architected logic is susceptible to errors. 
            All generated Intelligent Contracts must be manually audited.
          </span>
        </div>

        <div class="tabs-nav" v-if="userAddress">
          <button 
            @click="activeTab = 'forge'" 
            :class="['tab-btn', { active: activeTab === 'forge' }]"
          >
            >_ THE FORGE
          </button>
          <button 
            @click="activeTab = 'tasks'" 
            :class="['tab-btn', { active: activeTab === 'tasks' }]"
          >
            ACTIVE TASKS ({{ tasks.length }})
          </button>
        </div>

        <div v-if="activeTab === 'forge' || !userAddress" class="tab-content">
          <div class="prompt-line">
            <span class="user">user@root</span>:
            <span class="path">~/gen-forge</span>$ 
            <span class="cmd">architect --prompt</span>
          </div>
          
          <textarea 
            v-model="prompt" 
            placeholder="Describe the contract you want to build..."
            :disabled="isArchitecting"
            class="ubuntu-input"
          ></textarea>

          <div class="mode-toggle">
            <label class="toggle-label">
              <span class="toggle-text">
                Execution Mode: 
                <strong :class="isLeaderOnly ? 'text-warn' : 'text-safe'">
                  {{ isLeaderOnly ? 'FAST (Leader Only)' : 'SECURE (Full Consensus)' }}
                </strong>
              </span>
              <div class="switch-container">
                <input 
                  type="checkbox" 
                  v-model="isLeaderOnly" 
                  :disabled="isArchitecting"
                  class="hidden-checkbox"
                >
                <div class="slider"></div>
              </div>
            </label>
          </div>

          <button 
            @click="architectContract" 
            class="execute-btn"
            :disabled="!userAddress || !prompt"
          >
            <Rocket :size="18" />
            EXECUTE
          </button>
          
          <div class="logs">
            <p>> {{ statusMessage }}</p>
          </div>
        </div>

        <div v-if="activeTab === 'tasks' && userAddress" class="tab-content tasks-container">
          <div v-if="tasks.length === 0" class="empty-state">No active generations yet.</div>
          
          <div v-for="task in tasks" :key="task.id" class="task-card">
            <div class="task-header">
              <strong>Prompt:</strong> {{ task.prompt }}
            </div>
            <div class="task-status">
              <strong>Status:</strong> <span class="status-text">{{ task.status }}</span>
            </div>
            <button 
              v-if="task.code" 
              @click="generatedCode = task.code" 
              class="view-code-btn"
            >
              View in Output Pane
            </button>
          </div>
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
@import url('https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@400;700&display=swap');
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
  background-color: rgba(223, 72, 20, 0.1);
  border: 1px solid #df4814;
  color: #ffb4a1;
  padding: 12px 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.ai-warning strong { color: #df4814; }

/* Base Terminal Styles */
.toast-notification {
  position: fixed; top: 20px; right: 20px; padding: 15px 25px;
  border-radius: 4px; color: white; font-weight: bold; z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); border: 1px solid #ffffff33;
}
.toast-notification.error { background-color: #df4814; }
.toast-notification.success { background-color: #5eaa1a; }

.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.4s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(20px) translateY(-20px); opacity: 0; }

.window-header {
  background-color: #4a4a4a; height: 35px; display: flex; align-items: center;
  padding: 0 15px; border-radius: 8px 8px 0 0; position: relative;
}
.window-controls { display: flex; gap: 8px; }
.dot { width: 12px; height: 12px; border-radius: 50%; }
.close { background: #df4814; }
.minimize { background: #efb73e; }
.expand { background: #5eaa1a; }

.window-title { 
  position: absolute; left: 50%; transform: translateX(-50%); font-size: 0.85rem; color: #ccc; 
}
.header-actions { margin-left: auto; }
.connected-group { display: flex; align-items: center; gap: 10px; }
.sudo-btn {
  background: #df4814; color: white; border: none; padding: 3px 12px;
  border-radius: 4px; font-family: inherit; cursor: pointer;
}
.logout-btn { background-color: transparent; color: #df4814; border: 1px solid #df4814; }
.logout-btn:hover { background-color: #df4814; color: #fff; }

.terminal-body {
  flex: 1; background: rgba(48, 10, 36, 0.98); border: 1px solid #5e2750;
  display: grid; grid-template-columns: 1fr 1fr; padding: 20px; gap: 20px;
}

.pane { display: flex; flex-direction: column; gap: 10px; }
.user { color: #87ff5f; font-weight: bold; }
.path { color: #5fafff; font-weight: bold; }
.cmd { color: #fff; margin-left: 8px; }

/* TABS CSS */
.tabs-nav {
  display: flex; gap: 10px; border-bottom: 1px solid #5e2750; padding-bottom: 5px; margin-bottom: 10px;
}
.tab-btn {
  background: transparent; color: #666; border: none; font-family: 'Ubuntu Mono', monospace;
  font-size: 1.1rem; cursor: pointer; padding: 5px 10px; transition: 0.3s;
}
.tab-btn:hover { color: #fff; }
.tab-btn.active { color: #87ff5f; border-bottom: 2px solid #87ff5f; }

.tab-content { display: flex; flex-direction: column; gap: 15px; flex: 1; }

.ubuntu-input {
  flex: 1; min-height: 200px; background: rgba(0,0,0,0.2); border: 1px solid #5e2750;
  color: #38bdf8; padding: 15px; font-family: 'Ubuntu Mono', monospace;
  font-size: 1.1rem; resize: none; outline: none;
}

/* TASKS QUEUE CSS */
.tasks-container { overflow-y: auto; max-height: 400px; }
.task-card {
  background: rgba(0,0,0,0.4); border: 1px solid #5e2750; border-radius: 4px;
  padding: 15px; margin-bottom: 10px; text-align: left;
}
.task-header { color: #ccc; margin-bottom: 8px; }
.task-status { color: #efb73e; margin-bottom: 10px; font-size: 0.9rem; }
.status-text { color: #fff; }
.view-code-btn {
  background: transparent; color: #5eaa1a; border: 1px solid #5eaa1a;
  padding: 5px 10px; cursor: pointer; font-family: inherit; font-size: 0.9rem;
}
.view-code-btn:hover { background: #5eaa1a; color: #000; }
.empty-state { color: #666; font-style: italic; }

.execute-btn {
  background: #df4814; color: white; border: none; padding: 12px;
  font-family: inherit; font-weight: bold; display: flex; align-items: center;
  justify-content: center; gap: 10px; cursor: pointer;
}
.execute-btn:disabled { opacity: 0.5; }

.output-bg { background: #1c1c1c; border-radius: 4px; border: 1px solid #333; }
.pane-header { 
  background: #333; padding: 6px 15px; display: flex; align-items: center; 
  gap: 10px; font-size: 0.8rem; color: #aaa; 
}
.copy-btn { margin-left: auto; background: none; border: none; color: #38bdf8; cursor: pointer; }

.code-area { display: flex; padding: 15px; font-size: 1rem; overflow-y: auto; }
.lines { 
  display: flex; flex-direction: column; color: #555; padding-right: 15px; 
  border-right: 1px solid #333; text-align: right; 
}
pre { margin: 0; color: #f8f8f2; white-space: pre-wrap; }
.cursor { margin-left: 15px; animation: blink 1s infinite; color: #df4814; font-weight: bold; }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* --- TOGGLE SWITCH STYLES --- */
.mode-toggle { background: rgba(0,0,0,0.2); border: 1px solid #5e2750; padding: 10px 15px; border-radius: 4px; }
.toggle-label { display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-family: inherit; }
.toggle-text { color: #ccc; font-size: 0.95rem; }
.text-warn { color: #efb73e; }
.text-safe { color: #5eaa1a; }
.switch-container { position: relative; width: 46px; height: 24px; }
.hidden-checkbox { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: #4a4a4a; transition: .4s; border-radius: 24px; border: 1px solid #333;
}
.slider:before {
  position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px;
  background-color: #87ff5f; transition: .4s; border-radius: 50%;
}
.hidden-checkbox:checked + .slider { background-color: #df4814; }
.hidden-checkbox:checked + .slider:before { transform: translateX(22px); background-color: #fff; }
.hidden-checkbox:disabled + .slider { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 900px) { .terminal-body { grid-template-columns: 1fr; } }
</style>