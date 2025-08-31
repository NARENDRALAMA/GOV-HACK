// Agentic Community Assistant - AI Chatbot Frontend
class CommunityAssistant {
  constructor() {
    this.currentJourney = null;
    this.currentStep = 0;
    this.apiBase = "http://localhost:8000";
    this.conversationHistory = [];
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.addWelcomeMessage();
  }

  setupEventListeners() {
    // Chat form submission
    document.getElementById("chat-form").addEventListener("submit", (e) => {
      e.preventDefault();
      this.sendMessage();
    });

    // Enter key support for chat input
    document.getElementById("chat-input").addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
  }

  addWelcomeMessage() {
    // Welcome message is already in HTML, just ensure it's visible
    this.scrollToBottom();
  }

  async sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    this.addMessage(message, "user");

    // Clear input
    input.value = "";

    // Show typing indicator
    this.showTypingIndicator();

    try {
      // Send to AI assistant
      const response = await this.sendToAI(message);

      // Hide typing indicator
      this.hideTypingIndicator();

      // Add AI response to chat
      this.addMessage(
        response.response || response.fallback_response || "I'm here to help!",
        "agent"
      );

      // Handle journey creation if present
      if (response.journey_id) {
        this.currentJourney = response;
        this.showJourneyProgress(response);
      }

      // Handle any suggestions
      if (response.suggestions && response.suggestions.length > 0) {
        this.addSuggestions(response.suggestions);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      this.hideTypingIndicator();
      this.addMessage(
        "Sorry, I encountered an error. Please try again.",
        "agent"
      );
    }

    // Scroll to bottom
    this.scrollToBottom();
  }

  async sendToAI(message) {
    // If we have an existing journey, continue it
    if (this.currentJourney && this.currentJourney.journey_id) {
      return await this.continueConversation(message);
    } else {
      // Start new conversation
      return await this.startNewConversation(message);
    }
  }

  async startNewConversation(message) {
    const response = await fetch(`${this.apiBase}/ai/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async continueConversation(message) {
    const response = await fetch(`${this.apiBase}/ai/continue`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        journey_id: this.currentJourney.journey_id,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  addMessage(content, sender) {
    const chatMessages = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");

    messageDiv.className = `message ${sender}-message`;

    if (sender === "user") {
      messageDiv.innerHTML = `
        <div class="flex items-start justify-end">
          <div class="text-right">
            <p class="font-semibold text-white mb-1">You</p>
            <p>${this.escapeHtml(content)}</p>
          </div>
          <div class="bg-white text-blue-600 rounded-full w-8 h-8 flex items-center justify-center ml-3 flex-shrink-0">
            <i class="fas fa-user text-sm"></i>
          </div>
        </div>
      `;
    } else {
      messageDiv.innerHTML = `
        <div class="flex items-start">
          <div class="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0">
            <i class="fas fa-robot text-sm"></i>
          </div>
          <div>
            <p class="font-semibold text-blue-600 mb-1">AI Assistant</p>
            <div>${this.formatAgentMessage(content)}</div>
          </div>
        </div>
      `;
    }

    chatMessages.appendChild(messageDiv);

    // Store in conversation history
    this.conversationHistory.push({
      sender,
      content,
      timestamp: new Date().toISOString(),
    });
  }

  addSuggestions(suggestions) {
    const chatMessages = document.getElementById("chat-messages");
    const suggestionsDiv = document.createElement("div");

    suggestionsDiv.className = "message agent-message";
    suggestionsDiv.innerHTML = `
      <div class="flex items-start">
        <div class="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0">
          <i class="fas fa-lightbulb text-sm"></i>
        </div>
        <div>
          <p class="font-semibold text-blue-600 mb-1">Suggestions</p>
          <div class="mt-2 p-3 bg-green-50 rounded-lg">
            <ul class="space-y-1">
              ${suggestions
                .map(
                  (suggestion) => `
                <li class="text-green-700">• ${this.escapeHtml(suggestion)}</li>
              `
                )
                .join("")}
            </ul>
          </div>
        </div>
      </div>
    `;

    chatMessages.appendChild(suggestionsDiv);
  }

  formatAgentMessage(content) {
    // Handle different types of content
    if (typeof content === "string") {
      // Simple text message
      return `<p>${this.escapeHtml(content)}</p>`;
    } else if (content && typeof content === "object") {
      // Structured response
      let formatted = "";

      if (content.message) {
        formatted += `<p>${this.escapeHtml(content.message)}</p>`;
      }

      if (content.plan && content.plan.steps) {
        formatted += `<div class="mt-3 p-3 bg-blue-50 rounded-lg">`;
        formatted += `<p class="font-semibold text-blue-800 mb-2">Your Journey Plan:</p>`;
        formatted += `<ul class="space-y-1">`;
        content.plan.steps.forEach((step) => {
          formatted += `<li class="text-blue-700">• ${step.title}</li>`;
        });
        formatted += `</ul></div>`;
      }

      if (content.suggestions && content.suggestions.length > 0) {
        formatted += `<div class="mt-3 p-3 bg-green-50 rounded-lg">`;
        formatted += `<p class="font-semibold text-green-800 mb-2">Suggestions:</p>`;
        formatted += `<ul class="space-y-1">`;
        content.suggestions.forEach((suggestion) => {
          formatted += `<li class="text-green-700">• ${suggestion}</li>`;
        });
        formatted += `</ul></div>`;
      }

      return formatted;
    }

    return `<p>${this.escapeHtml(String(content))}</p>`;
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  showTypingIndicator() {
    document.getElementById("typing-indicator").style.display = "block";
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    document.getElementById("typing-indicator").style.display = "none";
  }

  scrollToBottom() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  showJourneyProgress(journey) {
    const progressSection = document.getElementById("journey-progress-section");
    progressSection.classList.remove("hidden");

    // Populate journey steps
    const stepsContainer = document.getElementById("journey-steps");
    stepsContainer.innerHTML = journey.plan.steps
      .map((step) => this.createStepCard(step))
      .join("");

    // Scroll to progress section
    progressSection.scrollIntoView({ behavior: "smooth" });
  }

  createStepCard(step) {
    const statusClass =
      step.status === "completed" ? "step-completed" : "step-active";
    const statusIcon =
      step.status === "completed" ? "fa-check-circle" : "fa-clock";

    return `
      <div class="bg-white border-2 border-gray-200 rounded-lg p-6 ${statusClass}">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-lg font-semibold text-gray-800">${step.title}</h4>
          <div class="text-2xl ${
            step.status === "completed" ? "text-green-500" : "text-blue-500"
          }">
            <i class="fas ${statusIcon}"></i>
          </div>
        </div>
        <p class="text-gray-600 mb-4">${step.description}</p>
        <div class="text-sm text-gray-500">
          <i class="fas fa-clock mr-1"></i>
          Processing time: ${step.processing_time || "Varies"}
        </div>
        ${
          step.status === "pending"
            ? `
          <button 
            onclick="app.processStep('${step.id}')"
            class="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors duration-200"
          >
            <i class="fas fa-play mr-2"></i>
            Start This Step
          </button>
        `
            : ""
        }
      </div>
    `;
  }

  async processStep(stepId) {
    if (!this.currentJourney) return;

    try {
      // Prefill the form for this step
      const prefillResponse = await fetch(
        `${this.apiBase}/prefill/${this.currentJourney.journey_id}/${stepId}`,
        { method: "POST" }
      );

      if (!prefillResponse.ok) {
        throw new Error(`HTTP error! status: ${prefillResponse.status}`);
      }

      const prefillData = await prefillResponse.json();

      // Show the form for review
      this.showStepForm(stepId, prefillData);
    } catch (error) {
      console.error("Error processing step:", error);
      this.addMessage(
        "Sorry, I couldn't process that step. Please try again.",
        "agent"
      );
    }
  }

  showStepForm(stepId, prefillData) {
    const formContainer = document.getElementById("current-step-form");
    formContainer.classList.remove("hidden");

    formContainer.innerHTML = `
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <h4 class="text-xl font-semibold text-blue-800 mb-4">
          <i class="fas fa-edit text-blue-500 mr-2"></i>
          Review Form Data
        </h4>
        <p class="text-blue-700 mb-4">${
          prefillData.review_text || "Please review the information below:"
        }</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          ${Object.entries(prefillData.data || {})
            .map(
              ([key, value]) => `
              <div>
                <label class="block text-sm font-medium text-blue-700 mb-2">${this.formatFieldLabel(
                  key
                )}</label>
                <input type="text" value="${value}" readonly class="w-full px-3 py-2 bg-blue-100 border border-blue-300 rounded-lg text-blue-800">
              </div>
            `
            )
            .join("")}
        </div>
        
        <div class="flex justify-between">
          <button onclick="app.grantConsent()" class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium">
            <i class="fas fa-check mr-2"></i>
            Grant Consent & Continue
          </button>
          <button onclick="app.goBack()" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium">
            <i class="fas fa-arrow-left mr-2"></i>
            Go Back
          </button>
        </div>
      </div>
    `;

    // Scroll to form
    formContainer.scrollIntoView({ behavior: "smooth" });
  }

  formatFieldLabel(key) {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  async grantConsent() {
    if (!this.currentJourney) return;

    try {
      // Grant consent
      const consentResponse = await fetch(
        `${this.apiBase}/consent/${this.currentJourney.journey_id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            journey_id: this.currentJourney.journey_id,
            consent: {
              scope: [this.currentJourney.plan.steps[this.currentStep].id],
              ttl_days: 30,
              signature: "User Consent",
            },
          }),
        }
      );

      if (!consentResponse.ok) {
        throw new Error(`HTTP error! status: ${consentResponse.status}`);
      }

      // Submit the form
      await this.submitCurrentStep();
    } catch (error) {
      console.error("Error granting consent:", error);
      this.addMessage(
        "Sorry, I couldn't process your consent. Please try again.",
        "agent"
      );
    }
  }

  async submitCurrentStep() {
    if (!this.currentJourney) return;

    try {
      const currentStep = this.currentJourney.plan.steps[this.currentStep];

      // Submit the form
      const submitResponse = await fetch(
        `${this.apiBase}/submit/${this.currentJourney.journey_id}/${currentStep.id}`,
        { method: "POST" }
      );

      if (!submitResponse.ok) {
        throw new Error(`HTTP error! status: ${submitResponse.status}`);
      }

      const submitData = await submitResponse.json();

      // Mark step as completed
      currentStep.status = "completed";

      // Add success message
      this.addMessage(
        `Great! I've successfully submitted your ${currentStep.title} application.`,
        "agent"
      );

      // Move to next step
      this.currentStep++;

      // Check if journey is complete
      if (this.currentStep >= this.currentJourney.plan.steps.length) {
        this.showJourneyComplete();
      } else {
        // Update the UI
        this.updateJourneyProgress();
      }

      // Hide the form
      document.getElementById("current-step-form").classList.add("hidden");
    } catch (error) {
      console.error("Error submitting step:", error);
      this.addMessage(
        "Sorry, I couldn't submit that step. Please try again.",
        "agent"
      );
    }
  }

  updateJourneyProgress() {
    const stepsContainer = document.getElementById("journey-steps");
    stepsContainer.innerHTML = this.currentJourney.plan.steps
      .map((step) => this.createStepCard(step))
      .join("");
  }

  showJourneyComplete() {
    const successSection = document.getElementById("success-section");
    successSection.classList.remove("hidden");

    // Populate summary
    const summaryContainer = document.getElementById("journey-summary");
    const completedSteps = this.currentJourney.plan.steps.filter(
      (step) => step.status === "completed"
    );

    summaryContainer.innerHTML = `
      <div class="text-left">
        <h5 class="font-semibold text-gray-700 mb-2">Journey Summary:</h5>
        <p class="text-gray-600 mb-3">You've successfully completed your ${
          this.currentJourney.life_event
        } journey!</p>
        
        <div class="mt-4 pt-4 border-t border-gray-200">
          <h6 class="font-semibold text-gray-700 mb-2">Services Completed:</h6>
          <ul class="space-y-1">
            ${completedSteps
              .map(
                (step) => `
                <li class="flex items-center text-green-600">
                  <i class="fas fa-check-circle mr-2"></i>
                  ${step.title}
                </li>
              `
              )
              .join("")}
          </ul>
        </div>
      </div>
    `;

    // Scroll to success section
    successSection.scrollIntoView({ behavior: "smooth" });
  }

  startNewChat() {
    // Reset everything
    this.currentJourney = null;
    this.currentStep = 0;
    this.conversationHistory = [];

    // Hide sections
    document.getElementById("success-section").classList.add("hidden");
    document.getElementById("journey-progress-section").classList.add("hidden");
    document.getElementById("current-step-form").classList.add("hidden");

    // Clear chat messages (keep welcome message)
    const chatMessages = document.getElementById("chat-messages");
    const welcomeMessage = chatMessages.querySelector(".agent-message");
    chatMessages.innerHTML = "";
    chatMessages.appendChild(welcomeMessage);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  goBack() {
    document.getElementById("current-step-form").classList.add("hidden");
  }

  showLoading() {
    document.getElementById("loading-overlay").classList.remove("hidden");
  }

  hideLoading() {
    document.getElementById("loading-overlay").classList.add("hidden");
  }
}

// Initialize the application
let app;
console.log("App.js loaded, setting up event listener...");

// Add a simple test function
window.testChat = function() {
  console.log("Test function called");
  if (app) {
    console.log("App is initialized, testing sendMessage");
    // Simulate a test message
    const testInput = document.getElementById("chat-input");
    if (testInput) {
      testInput.value = "test message";
      app.sendMessage();
    } else {
      console.error("Test input not found");
    }
  } else {
    console.log("App not initialized yet");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, creating CommunityAssistant...");
  try {
    app = new CommunityAssistant();
    console.log("CommunityAssistant created successfully");
    
    // Now set up event listeners after DOM is ready
    app.setupEventListeners();
    
    // Test that everything is working
    console.log("Testing form elements:");
    console.log("Chat form:", document.getElementById("chat-form"));
    console.log("Chat input:", document.getElementById("chat-input"));
    console.log("Chat messages:", document.getElementById("chat-messages"));
    
    // Test the AI endpoint
    console.log("Testing AI endpoint...");
    fetch("http://localhost:8000/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "test" })
    })
    .then(response => response.json())
    .then(data => console.log("AI test response:", data))
    .catch(error => console.error("AI test error:", error));
    
  } catch (error) {
    console.error("Error creating CommunityAssistant:", error);
  }
});

// Global functions for onclick handlers
function startNewChat() {
  console.log("startNewChat called");
  if (app) {
    app.startNewChat();
  } else {
    console.error("App not initialized");
  }
}
