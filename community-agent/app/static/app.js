// Agentic Community Assistant - Frontend Application
class CommunityAssistant {
  constructor() {
    this.currentJourney = null;
    this.currentStep = 0;
    this.apiBase = "http://localhost:8000";
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setDefaultDates();
  }

  setupEventListeners() {
    // Form submission
    document.getElementById("intake-form").addEventListener("submit", (e) => {
      e.preventDefault();
      this.submitIntake();
    });
  }

  setDefaultDates() {
    // Set default dates for demo purposes
    const today = new Date();
    const babyDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 days ago

    document.getElementById("parent1_dob").value = "1990-01-01";
    document.getElementById("baby_dob").value = babyDate
      .toISOString()
      .split("T")[0];
  }

  startJourney() {
    document.getElementById("welcome-section").classList.add("hidden");
    document.getElementById("journey-form-section").classList.remove("hidden");

    // Smooth scroll to form
    document.getElementById("journey-form-section").scrollIntoView({
      behavior: "smooth",
    });
  }

  async submitIntake() {
    this.showLoading();

    try {
      // Collect form data
      const formData = this.collectFormData();

      // Submit to API
      const response = await fetch(`${this.apiBase}/intake`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      this.currentJourney = result;

      // Show journey progress
      this.showJourneyProgress();
    } catch (error) {
      console.error("Error submitting intake:", error);
      this.showError("Failed to create journey. Please try again.");
    } finally {
      this.hideLoading();
    }
  }

  collectFormData() {
    return {
      parent1: {
        full_name: document.getElementById("parent1_name").value,
        dob: document.getElementById("parent1_dob").value,
        email: document.getElementById("parent1_email").value || null,
        phone: document.getElementById("parent1_phone").value || null,
      },
      parent2: document.getElementById("parent2_name").value
        ? {
            full_name: document.getElementById("parent2_name").value,
            dob: document.getElementById("parent2_dob").value || null,
          }
        : null,
      baby: {
        name: document.getElementById("baby_name").value || null,
        sex: document.getElementById("baby_sex").value || null,
        dob: document.getElementById("baby_dob").value,
        place_of_birth: document.getElementById("place_of_birth").value || null,
        parents: [],
      },
      address: document.getElementById("address_line1").value
        ? {
            line1: document.getElementById("address_line1").value,
            suburb: document.getElementById("suburb").value || null,
            state: document.getElementById("state").value,
            postcode: document.getElementById("postcode").value || null,
          }
        : null,
      preferred_language: "en",
      accessibility: [],
    };
  }

  showJourneyProgress() {
    document.getElementById("journey-form-section").classList.add("hidden");
    document
      .getElementById("journey-progress-section")
      .classList.remove("hidden");

    this.renderJourneySteps();
    this.processCurrentStep();
  }

  renderJourneySteps() {
    const stepsContainer = document.getElementById("journey-steps");
    stepsContainer.innerHTML = "";

    this.currentJourney.plan.steps.forEach((step, index) => {
      const stepCard = this.createStepCard(step, index);
      stepsContainer.appendChild(stepCard);
    });
  }

  createStepCard(step, index) {
    const card = document.createElement("div");
    card.className = `bg-white border-2 rounded-xl p-6 card-hover ${
      index === this.currentStep
        ? "border-blue-500 shadow-lg"
        : "border-gray-200"
    }`;

    const statusClass =
      step.status === "completed"
        ? "step-completed"
        : index === this.currentStep
        ? "step-active"
        : "bg-gray-100 text-gray-600";

    card.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h4 class="text-xl font-semibold text-gray-800">${
                  step.title
                }</h4>
                <span class="px-3 py-1 rounded-full text-sm font-medium ${statusClass}">
                    ${
                      step.status === "completed"
                        ? "✓ Completed"
                        : index === this.currentStep
                        ? "🔄 In Progress"
                        : "⏳ Pending"
                    }
                </span>
            </div>
            <p class="text-gray-600 mb-4">
                ${this.getStepDescription(step.id)}
            </p>
            ${
              step.status === "completed"
                ? `<div class="text-green-600 font-medium">✓ Completed successfully</div>`
                : index === this.currentStep
                ? `<button onclick="app.processCurrentStep()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    Continue
                </button>`
                : `<div class="text-gray-400">Waiting to start</div>`
            }
        `;

    return card;
  }

  getStepDescription(stepId) {
    const descriptions = {
      birth_reg:
        "Register your baby's birth with NSW Registry of Births, Deaths and Marriages. This is required within 60 days of birth.",
      medicare_enrolment:
        "Enrol your newborn for Medicare coverage. Newborns are automatically covered under their parent's Medicare card for the first 12 months.",
    };
    return (
      descriptions[stepId] || "Complete this step to continue your journey."
    );
  }

  async processCurrentStep() {
    if (this.currentStep >= this.currentJourney.plan.steps.length) {
      this.showSuccess();
      return;
    }

    const currentStepData = this.currentJourney.plan.steps[this.currentStep];

    try {
      // Prefill the form
      const prefillResponse = await fetch(
        `${this.apiBase}/prefill/${this.currentJourney.journey_id}/${currentStepData.id}`,
        {
          method: "POST",
        }
      );

      if (!prefillResponse.ok) {
        throw new Error(`HTTP error! status: ${prefillResponse.status}`);
      }

      const prefillData = await prefillResponse.json();

      // Show the form for review
      this.showStepForm(currentStepData, prefillData);
    } catch (error) {
      console.error("Error processing step:", error);
      this.showError("Failed to process step. Please try again.");
    }
  }

  showStepForm(step, prefillData) {
    const formContainer = document.getElementById("current-step-form");
    formContainer.classList.remove("hidden");

    formContainer.innerHTML = `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <h4 class="text-xl font-semibold text-blue-800 mb-4">
                    <i class="fas fa-edit text-blue-500 mr-2"></i>
                    Review ${step.title}
                </h4>
                <p class="text-blue-700 mb-4">${prefillData.review_text}</p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    ${Object.entries(prefillData.data)
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
    this.showLoading();

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
      this.showError("Failed to grant consent. Please try again.");
      this.hideLoading();
    }
  }

  async submitCurrentStep() {
    try {
      const currentStepData = this.currentJourney.plan.steps[this.currentStep];

      // Submit the form
      const submitResponse = await fetch(
        `${this.apiBase}/submit/${this.currentJourney.journey_id}/${currentStepData.id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        }
      );

      if (!submitResponse.ok) {
        throw new Error(`HTTP error! status: ${submitResponse.status}`);
      }

      const submitResult = await submitResponse.json();

      // Mark step as completed
      currentStepData.status = "completed";

      // Move to next step
      this.currentStep++;

      // Update UI
      this.renderJourneySteps();
      document.getElementById("current-step-form").classList.add("hidden");

      // Check if journey is complete
      if (this.currentStep >= this.currentJourney.plan.steps.length) {
        this.showSuccess();
      } else {
        // Process next step
        setTimeout(() => this.processCurrentStep(), 1000);
      }
    } catch (error) {
      console.error("Error submitting step:", error);
      this.showError("Failed to submit step. Please try again.");
    } finally {
      this.hideLoading();
    }
  }

  showSuccess() {
    document.getElementById("journey-progress-section").classList.add("hidden");
    document.getElementById("success-section").classList.remove("hidden");

    // Populate journey summary
    this.populateJourneySummary();

    // Scroll to success
    document
      .getElementById("success-section")
      .scrollIntoView({ behavior: "smooth" });
  }

  populateJourneySummary() {
    const summaryContainer = document.getElementById("journey-summary");

    const completedSteps = this.currentJourney.plan.steps.filter(
      (step) => step.status === "completed"
    );

    summaryContainer.innerHTML = `
            <div class="text-left">
                <h5 class="font-semibold text-gray-800 mb-3">Journey Summary</h5>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Journey ID:</span>
                        <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">${
                          this.currentJourney.journey_id
                        }</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Steps Completed:</span>
                        <span class="text-green-600 font-medium">${
                          completedSteps.length
                        }/${this.currentJourney.plan.steps.length}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Completed On:</span>
                        <span class="text-gray-800">${new Date().toLocaleDateString()}</span>
                    </div>
                </div>
                
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
  }

  startNewJourney() {
    // Reset everything
    this.currentJourney = null;
    this.currentStep = 0;

    // Reset form
    document.getElementById("intake-form").reset();
    this.setDefaultDates();

    // Show welcome section
    document.getElementById("success-section").classList.add("hidden");
    document.getElementById("welcome-section").classList.remove("hidden");

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

  showError(message) {
    // Create and show error notification
    const notification = document.createElement("div");
    notification.className =
      "fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50";
    notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                <span>${message}</span>
            </div>
        `;

    document.body.appendChild(notification);

    // Remove after 5 seconds
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
}

// Initialize the application
let app;
console.log("App.js loaded, setting up event listener...");
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, creating CommunityAssistant...");
  try {
    app = new CommunityAssistant();
    console.log("CommunityAssistant created successfully");
  } catch (error) {
    console.error("Error creating CommunityAssistant:", error);
  }
});

// Global functions for onclick handlers
function startJourney() {
  console.log("startJourney called");
  if (app) {
    console.log("App exists, calling startJourney");
    app.startJourney();
  } else {
    console.error("App not initialized yet");
    alert("App not ready yet. Please wait a moment and try again.");
  }
}

function startNewJourney() {
  app.startNewJourney();
}
