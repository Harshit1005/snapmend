<template>
  <div class="camera-wrapper">

    <!-- Hidden canvas — always rendered for capture -->
    <canvas ref="canvas" style="display:none"></canvas>

    <!-- State: Loading -->
    <div v-if="state === 'loading'" class="state-loading">
      <div class="mini-spinner"></div>
      <p>Opening camera...</p>
    </div>

    <!-- State: Live viewfinder -->
    <div v-else-if="state === 'live'" class="viewfinder-container">
      <video ref="video" autoplay playsinline muted class="viewfinder-video"></video>

      <!-- Corner framing brackets -->
      <div class="frame-overlay" aria-hidden="true">
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
        <p class="frame-hint">Point at the pavement damage</p>
      </div>

      <!-- Shutter bar -->
      <div class="capture-bar">
        <button type="button" class="shutter-btn" @click="capture" aria-label="Take photo">
          <div class="shutter-ring"><div class="shutter-inner"></div></div>
        </button>
        <button
          v-if="hasMultipleCameras"
          type="button"
          class="flip-btn"
          @click="switchCamera"
          aria-label="Flip camera"
        >
          <span class="material-symbols-outlined" style="font-size:22px">flip_camera_ios</span>
        </button>
      </div>
    </div>

    <!-- State: Preview after capture -->
    <div v-else-if="state === 'preview'" class="preview-container">
      <img :src="previewUrl" class="preview-img" alt="Captured pavement photo" />

      <div class="captured-badge">
        <span class="material-symbols-outlined" style="font-size:16px;color:#2e7d32">check_circle</span>
        Photo captured
      </div>

      <div class="preview-actions">
        <button type="button" class="retake-btn" @click="retake">
          <span class="material-symbols-outlined" style="font-size:18px">replay</span>
          Retake
        </button>
        <button type="button" class="use-btn" @click="usePhoto">
          Use Photo ✓
        </button>
      </div>
    </div>

    <!-- State: Confirmed — show thumbnails -->
    <div v-else-if="state === 'confirmed'" class="confirmed-container">
      <div class="confirmed-thumb-row">
        <div v-for="(url, i) in confirmedPreviews" :key="i" class="confirmed-thumb">
          <img :src="url" alt="Captured photo" />
          <div class="thumb-ok">✓</div>
        </div>
        <button type="button" class="add-more-btn" @click="addMore" aria-label="Add more photos">
          <span class="material-symbols-outlined" style="font-size:24px">add_a_photo</span>
        </button>
      </div>
      <p class="confirmed-label">
        {{ capturedFiles.length }} photo{{ capturedFiles.length !== 1 ? 's' : '' }} ready
        <span style="opacity:0.5"> · tap + for more</span>
      </p>
    </div>

    <!-- State: Error / Camera denied — fallback file picker -->
    <div v-else-if="state === 'error'" class="fallback-container">
      <label class="fallback-label" :for="inputId">
        <span style="font-size:2.2rem">📷</span>
        <span style="font-size:14px;font-weight:600">Select Pavement Photos</span>
        <span style="font-size:11px;opacity:0.55;margin-top:2px">Camera unavailable — tap to browse files</span>
      </label>
      <input
        :id="inputId"
        type="file"
        multiple
        accept="image/*"
        @change="handleFallbackSelect"
        style="display:none"
      />
    </div>

  </div>
</template>

<script>
export default {
  name: 'CameraCapture',
  emits: ['update:files', 'update:previews'],

  data() {
    return {
      state: 'loading',
      stream: null,
      previewUrl: null,
      capturedFiles: [],
      confirmedPreviews: [],
      hasMultipleCameras: false,
      facingMode: 'environment',
      inputId: 'cam-fallback-' + Math.random().toString(36).slice(2, 8),
    }
  },

  async mounted() {
    await this.detectCameras()
    await this.startCamera()
  },

  beforeUnmount() {
    this.stopStream()
  },

  methods: {
    // ── Camera setup ─────────────────────────────────────────────
    async detectCameras() {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        this.hasMultipleCameras = devices.filter(d => d.kind === 'videoinput').length > 1
      } catch {
        this.hasMultipleCameras = false
      }
    },

    async startCamera() {
      this.state = 'loading'
      if (!navigator.mediaDevices?.getUserMedia) {
        this.state = 'error'
        return
      }
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: this.facingMode, width: { ideal: 1920 }, height: { ideal: 1080 } },
          audio: false,
        })
        this.state = 'live'
        // Must wait for DOM to render the <video> element
        await this.$nextTick()
        if (this.$refs.video) {
          this.$refs.video.srcObject = this.stream
          await this.$refs.video.play().catch(() => {})
        }
      } catch (err) {
        console.warn('CameraCapture: getUserMedia failed —', err.name, err.message)
        this.state = 'error'
      }
    },

    async switchCamera() {
      this.stopStream()
      this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment'
      await this.startCamera()
    },

    stopStream() {
      this.stream?.getTracks().forEach(t => t.stop())
      this.stream = null
    },

    // ── Capture flow ──────────────────────────────────────────────
    capture() {
      const video = this.$refs.video
      const canvas = this.$refs.canvas   // always mounted — outside v-if
      if (!video || !canvas) {
        console.warn('CameraCapture: video or canvas ref missing at capture time')
        return
      }
      if (video.videoWidth === 0) {
        console.warn('CameraCapture: video not ready yet (videoWidth = 0)')
        return
      }

      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)

      this.previewUrl = canvas.toDataURL('image/jpeg', 0.92)
      this.state = 'preview'
      this.stopStream()   // save battery while reviewing
    },

    retake() {
      this.previewUrl = null
      this.startCamera()
    },

    async usePhoto() {
      // data URL → Blob → File
      const res = await fetch(this.previewUrl)
      const blob = await res.blob()
      const name = `pavement-${Date.now()}.jpg`
      const file = new File([blob], name, { type: 'image/jpeg' })

      this.capturedFiles = [...this.capturedFiles, file]
      this.confirmedPreviews = [...this.confirmedPreviews, this.previewUrl]

      this.$emit('update:files', this.capturedFiles)
      this.$emit('update:previews', this.confirmedPreviews)

      this.state = 'confirmed'
    },

    addMore() {
      this.previewUrl = null
      this.startCamera()
    },

    // ── Fallback (file picker) ────────────────────────────────────
    handleFallbackSelect(event) {
      const files = Array.from(event.target.files)
      const previews = files.map(f => URL.createObjectURL(f))
      this.capturedFiles = files
      this.confirmedPreviews = previews
      this.state = 'confirmed'
      this.$emit('update:files', files)
      this.$emit('update:previews', previews)
    },
  },
}
</script>

<style scoped>
/* ── Shell ── */
.camera-wrapper {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 16px;
  overflow: hidden;
  background: #0a0a0a;
  position: relative;
}

/* ── Shared full-size div ── */
.viewfinder-container,
.preview-container,
.confirmed-container,
.fallback-container,
.state-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* ── Loading ── */
.state-loading { color: rgba(255,255,255,0.65); font-size: 13px; gap: 12px; }
.mini-spinner {
  width: 32px; height: 32px;
  border: 3px solid rgba(255,255,255,0.15);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Viewfinder ── */
.viewfinder-container { justify-content: flex-start; }
.viewfinder-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Corner brackets */
.frame-overlay { position: absolute; inset: 0; pointer-events: none; }
.corner {
  position: absolute;
  width: 26px; height: 26px;
  border-color: rgba(255,255,255,0.8);
  border-style: solid;
}
.corner.tl { top:14px; left:14px;  border-width:3px 0 0 3px; border-radius:4px 0 0 0; }
.corner.tr { top:14px; right:14px; border-width:3px 3px 0 0; border-radius:0 4px 0 0; }
.corner.bl { bottom:80px; left:14px;  border-width:0 0 3px 3px; border-radius:0 0 0 4px; }
.corner.br { bottom:80px; right:14px; border-width:0 3px 3px 0; border-radius:0 0 4px 0; }
.frame-hint {
  position: absolute;
  bottom: 82px; left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.4);
  color: rgba(255,255,255,0.8);
  font-size: 12px; font-weight: 500;
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
}

/* Shutter bar */
.capture-bar {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 80px;
  background: linear-gradient(to top, rgba(0,0,0,0.6), transparent);
  display: flex; align-items: center; justify-content: center;
  z-index: 2;
}
.shutter-btn {
  background: none; border: none; cursor: pointer; padding: 0;
  transition: transform 0.1s;
}
.shutter-btn:active { transform: scale(0.9); }
.shutter-ring {
  width: 64px; height: 64px; border-radius: 50%;
  border: 3px solid white;
  display: flex; align-items: center; justify-content: center;
}
.shutter-inner { width: 52px; height: 52px; border-radius: 50%; background: white; }
.flip-btn {
  position: absolute; right: 20px;
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.18);
  border: none; color: white; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.flip-btn:hover { background: rgba(255,255,255,0.32); }

/* ── Preview ── */
.preview-container { justify-content: flex-start; }
.preview-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.captured-badge {
  position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
  background: rgba(255,255,255,0.93);
  border-radius: 20px; padding: 5px 14px;
  font-size: 13px; font-weight: 600; color: #2e7d32;
  display: flex; align-items: center; gap: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  white-space: nowrap; z-index: 2;
}
.preview-actions {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 76px;
  background: linear-gradient(to top, rgba(0,0,0,0.65), transparent);
  display: flex; align-items: center; justify-content: center;
  gap: 14px; z-index: 2;
}
.retake-btn {
  background: rgba(255,255,255,0.18);
  border: 1.5px solid rgba(255,255,255,0.5);
  color: white; border-radius: 24px;
  padding: 9px 20px; font-size: 14px; font-weight: 600;
  cursor: pointer;
  display: flex; align-items: center; gap: 6px;
}
.use-btn {
  background: #b02a26; border: none; color: white;
  border-radius: 24px; padding: 10px 26px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  box-shadow: 0 2px 12px rgba(176,42,38,0.45);
}

/* ── Confirmed ── */
.confirmed-container { gap: 14px; }
.confirmed-thumb-row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.confirmed-thumb {
  position: relative;
  width: 80px; height: 80px; border-radius: 10px;
  overflow: hidden; border: 2px solid #2e7d32;
}
.confirmed-thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-ok {
  position: absolute; top: 4px; right: 4px;
  background: #2e7d32; color: white;
  border-radius: 50%; width: 18px; height: 18px;
  font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.add-more-btn {
  width: 80px; height: 80px; border-radius: 10px;
  border: 2px dashed rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.65);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: border-color 0.15s;
}
.add-more-btn:hover { border-color: rgba(255,255,255,0.6); }
.confirmed-label { font-size: 13px; color: rgba(255,255,255,0.65); font-weight: 500; text-align: center; }

/* ── Fallback ── */
.fallback-container { padding: 16px; }
.fallback-label {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  cursor: pointer;
  background: rgba(255,255,255,0.06);
  border: 2px dashed rgba(255,255,255,0.25);
  border-radius: 12px; padding: 28px 32px;
  color: white; width: 100%; box-sizing: border-box; text-align: center;
  transition: border-color 0.2s;
}
.fallback-label:hover { border-color: rgba(255,255,255,0.5); }
</style>
