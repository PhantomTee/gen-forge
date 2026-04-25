<template>
  <div class="terminal-container">
    <header class="window-header">
      <div class="window-controls">
        <span class="dot close"></span>
        <span class="dot minimize"></span>
        <span class="dot expand"></span>
      </div>
      <div class="window-title">phantomx@THALHAT: ~/gen-forge</div>
      <div class="header-actions">
        <div v-if="userAddress" class="user-id">
          CONNECTED: {{ userAddress.substring(0, 6) }}...
        </div>
        <button v-else @click="connectWallet" class="auth-btn">sudo login</button>
      </div>
    </header>

    <main class="terminal-body">
      <section class="terminal-pane input-pane">
        <div class="prompt-line">
          <span class="user-path">phantomx@THALHAT</span>:<span class="dir">~/gen-forge</span>$ 
          <span class="cmd">architect --prompt</span>
        </div>
        
        <textarea 
          v-model="prompt" 
          placeholder="Enter contract description here..."
          :disabled="isArchitecting"
          class="ubuntu-input"
        ></textarea>

        <div class="actions">
          <button 
            @click="architectContract" 
            class="execute-btn"
            :disabled="isArchitecting || !userAddress"
          >
            [ {{ isArchitecting ? 'RUNNING...' : 'EXECUTE' }} ]
          </button>
        </div>
        
        <div class="system-logs">
          <p class="log-entry">> {{ statusMessage }}</p>
        </div>
      </section>

      <section class="terminal-pane output-pane">
        <div class="pane-label">/var/www/generated_contract.py</div>
        <div class="code-editor">
          <div class="line-numbers">
            <span v-for="n in 15" :key="n">{{ n }}</span>
          </div>
          <pre v-if="generatedCode"><code>{{ generatedCode }}</code></pre>
          <div v-else class="cursor-blink">_</div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* UBUNTU FONT IMPORT */
@import url('https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@400;700&display=swap');

.terminal-container {
  min-height: 100vh;
  background-color: #300a24; /* Official Ubuntu Purple */
  color: #ffffff;
  font-family: 'Ubuntu Mono', monospace;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
}

/* WINDOW HEADER STYLING */
.window-header {
  background-color: #4a4a4a;
  height: 35px;
  display: flex;
  align-items: center;
  padding: 0 15px;
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid #222;
  position: relative;
}

.window-controls {
  display: flex;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.close { background: #df4814; }
.minimize { background: #efb73e; }
.expand { background: #5eaa1a; }

.window-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.9rem;
  color: #ddd;
}

.header-actions {
  margin-left: auto;
  font-size: 0.8rem;
}

/* TERMINAL CORE */
.terminal-body {
  flex: 1;
  background-color: rgba(48, 10, 36, 0.95);
  border: 1px solid #5e2750;
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 20px;
  gap: 20px;
}

.terminal-pane {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* INPUT SECTION */
.user-path { color: #87ff5f; font-weight: bold; }
.dir { color: #5fafff; font-weight: bold; }
.cmd { color: #ffffff; margin-left: 8px; }

.ubuntu-input {
  flex: 1;
  background: transparent;
  border: 1px solid #5e2750;
  color: #38bdf8;
  padding: 15px;
  font-family: 'Ubuntu Mono', monospace;
  font-size: 1.1rem;
  outline: none;
  resize: none;
}

.execute-btn {
  background: #df4814;
  color: white;
  border: none;
  padding: 10px 20px;
  font-family: inherit;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.execute-btn:hover:not(:disabled) { background: #ff5c26; }
.execute-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* CODE EDITOR SECTION */
.output-pane {
  background: #1c1c1c;
  border-radius: 4px;
  border: 1px solid #333;
}

.pane-label {
  background: #333;
  padding: 5px 15px;
  font-size: 0.8rem;
  color: #aaa;
}

.code-editor {
  display: flex;
  padding: 15px;
  font-size: 1rem;
  overflow: auto;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  color: #555;
  padding-right: 15px;
  border-right: 1px solid #333;
  text-align: right;
  user-select: none;
}

pre {
  margin: 0;
  padding-left: 15px;
  color: #f8f8f2;
}

.system-logs {
  font-size: 0.85rem;
  color: #aea79f;
  margin-top: 10px;
}

/* CURSOR BLINK */
.cursor-blink {
  margin-left: 15px;
  animation: blink 1s infinite;
}

@keyframes blink { 
  0% { opacity: 1; } 
  50% { opacity: 0; } 
  100% { opacity: 1; } 
}

@media (max-width: 900px) {
  .terminal-body { grid-template-columns: 1fr; }
}
</style>