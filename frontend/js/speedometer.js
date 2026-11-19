/**
 * DataFix Speedometer & Telemetry Engine
 * Renders real-time telemetry, needle animation, RPM gauge, Nitro booster, and Web Audio SFX.
 */

class TelemetryEngine {
  constructor() {
    this.audioContext = null;
    this.soundEnabled = true;
    this.currentScore = 78;
    this.targetScore = 78;
    this.needleElement = null;
    this.mphValueElement = null;
    this.rpmBarElement = null;
    this.zoneLabelElement = null;
    this.boostActive = false;
  }

  init() {
    this.needleElement = document.getElementById("speedometer-needle");
    this.mphValueElement = document.getElementById("speedometer-mph-value");
    this.rpmBarElement = document.getElementById("rpm-bar-fill");
    this.zoneLabelElement = document.getElementById("speedometer-zone-label");

    // Initialize Web Audio on first user interaction
    const initAudio = () => {
      if (!this.audioContext) {
        try {
          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          if (AudioContextClass) {
            this.audioContext = new AudioContextClass();
          }
        } catch (e) {
          console.warn("Web Audio not supported or blocked", e);
        }
      }
      document.removeEventListener("click", initAudio);
      document.removeEventListener("keydown", initAudio);
    };

    document.addEventListener("click", initAudio);
    document.addEventListener("keydown", initAudio);

    this.updateDisplay(this.currentScore);
  }

  setSoundEnabled(enabled) {
    this.soundEnabled = enabled;
    return this.soundEnabled;
  }

  toggleSound() {
    this.soundEnabled = !this.soundEnabled;
    return this.soundEnabled;
  }

  /**
   * Updates quality score with smooth needle animation.
   * Score is 0 - 100%, mapped to precision 0 - 100 scale.
   * Needle angle sweeps from -120 deg (0 / 0%) to +120 deg (100 / 100%).
   */
  updateDisplay(score, playAudio = false) {
    const clampedScore = Math.max(0, Math.min(100, Math.round(score)));
    this.currentScore = clampedScore;

    // Angle mapping: -120deg to +120deg (span of 240 degrees)
    const angle = -120 + (clampedScore / 100) * 240;
    const speedVal = clampedScore; // 0 to 100 scale
    const rpm = clampedScore === 0 ? 0 : Math.round(1000 + (clampedScore / 100) * 7000);

    if (this.needleElement) {
      this.needleElement.style.transform = `rotate(${angle}deg)`;
    }

    if (this.mphValueElement) {
      this.mphValueElement.textContent = speedVal;
    }

    const scoreDisplay = document.getElementById("speedometer-score-display");
    if (scoreDisplay) {
      scoreDisplay.textContent = clampedScore === 0 ? "--" : `${clampedScore}%`;
    }

    if (this.rpmBarElement) {
      const rpmPercent = Math.min(100, (rpm / 8000) * 100);
      this.rpmBarElement.style.width = `${rpmPercent}%`;
    }

    const rpmTextVal = document.getElementById("rpm-text-val");
    if (rpmTextVal) {
      rpmTextVal.textContent = clampedScore === 0 ? "0 / 8,000" : `${rpm.toLocaleString()} / 8,000`;
    }

    if (this.zoneLabelElement) {
      let zone = "RED ZONE // HIGH ANOMALY";
      let colorClass = "zone-critical";
      if (clampedScore === 0) {
        zone = "STANDBY // AWAITING DATASET";
        colorClass = "zone-standby";
      } else if (clampedScore >= 95) {
        zone = "MAX PURITY // TURBO CHARGED";
        colorClass = "zone-optimal";
      } else if (clampedScore >= 80) {
        zone = "OPTIMAL // STABLE CRUISE";
        colorClass = "zone-good";
      } else if (clampedScore >= 60) {
        zone = "WARNING // DEGRADED FLOW";
        colorClass = "zone-warning";
      }
      this.zoneLabelElement.textContent = zone;
      this.zoneLabelElement.className = `zone-label ${colorClass}`;
    }

    if (playAudio && this.soundEnabled) {
      if (clampedScore >= 95) {
        this.playSuccessChime();
      } else if (clampedScore < 60) {
        this.playWarningAlert();
      } else {
        this.playRevSFX(mph);
      }
    }
  }

  triggerBoost(onComplete) {
    if (this.boostActive) return;
    this.boostActive = true;

    if (this.soundEnabled) {
      this.playNitroWhoosh();
    }

    const boosterBtn = document.getElementById("nitro-booster-btn");
    if (boosterBtn) {
      boosterBtn.classList.add("nitro-pulsing");
    }

    const initialScore = this.currentScore;
    let tempScore = initialScore;
    const interval = setInterval(() => {
      tempScore = Math.min(100, tempScore + 4);
      this.updateDisplay(tempScore, false);
      if (tempScore >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          if (boosterBtn) boosterBtn.classList.remove("nitro-pulsing");
          this.boostActive = false;
          if (typeof onComplete === "function") {
            onComplete();
          }
        }, 600);
      }
    }, 40);
  }

  // Synthesis SFX via Web Audio API (zero external audio file dependencies)
  ensureContext() {
    if (!this.audioContext) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        this.audioContext = new AudioContextClass();
      }
    }
    if (this.audioContext && this.audioContext.state === "suspended") {
      this.audioContext.resume();
    }
    return this.audioContext;
  }

  playRevSFX(speedVal = 100) {
    const ctx = this.ensureContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const baseFreq = 70 + (speedVal / 100) * 140;

      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(baseFreq, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.5, ctx.currentTime + 0.3);

      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) {
      console.warn("Audio SFX error", e);
    }
  }

  playNitroWhoosh() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    try {
      // Noise buffer for nitro hiss
      const bufferSize = ctx.sampleRate * 0.8;
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }

      const noise = ctx.createBufferSource();
      noise.buffer = buffer;

      const filter = ctx.createBiquadFilter();
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(1000, ctx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(3200, ctx.currentTime + 0.5);

      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.8);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      noise.start();
      noise.stop(ctx.currentTime + 0.8);
    } catch (e) {
      console.warn("Audio SFX error", e);
    }
  }

  playSuccessChime() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    try {
      const freqs = [523.25, 659.25, 783.99, 1046.50]; // C Major arpeggio
      freqs.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.08);

        gain.gain.setValueAtTime(0.08, ctx.currentTime + i * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.08 + 0.5);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime + i * 0.08);
        osc.stop(ctx.currentTime + i * 0.08 + 0.5);
      });
    } catch (e) {
      console.warn("Audio SFX error", e);
    }
  }

  playWarningAlert() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "square";
      osc.frequency.setValueAtTime(300, ctx.currentTime);
      osc.frequency.setValueAtTime(220, ctx.currentTime + 0.15);

      gain.gain.setValueAtTime(0.06, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } catch (e) {
      console.warn("Audio SFX error", e);
    }
  }
}

window.telemetry = new TelemetryEngine();
