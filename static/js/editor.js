// Image Editor Functionality

let currentImage = null;
let isProcessing = false;

// --- Undo/Redo stacks ---
let undoStack = [];
let redoStack = [];

document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const uploadForm = document.getElementById('upload-form');
  const uploadInput = document.getElementById('upload-input');
  const uploadContainer = document.getElementById('upload-container');
  const editorContainer = document.getElementById('editor-container');
  const previewContainer = document.getElementById('preview-container');
  const previewImg = document.getElementById('preview-img');
  const resetButton = document.getElementById('reset-button');
  const downloadButton = document.getElementById('download-button');
  const toolButtons = document.querySelectorAll('.tool-btn');
  const controlsContainer = document.getElementById('controls-container');
  const undoButton = document.getElementById('undo-button');
  const redoButton = document.getElementById('redo-button');
  
  // Setup drag and drop
  if (uploadContainer) {
    uploadContainer.addEventListener('dragover', function(e) {
      e.preventDefault();
      uploadContainer.classList.add('drag-active');
    });
    
    uploadContainer.addEventListener('dragleave', function() {
      uploadContainer.classList.remove('drag-active');
    });
    
    uploadContainer.addEventListener('drop', function(e) {
      e.preventDefault();
      uploadContainer.classList.remove('drag-active');
      
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        uploadInput.files = e.dataTransfer.files;
        const event = new Event('change');
        uploadInput.dispatchEvent(event);
      }
    });
  }
  
  // Handle file upload
  if (uploadInput) {
    uploadInput.addEventListener('change', function() {
      if (this.files && this.files[0]) {
        const file = this.files[0];
        
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!validTypes.includes(file.type)) {
          showAlert('Please select a valid image file (JPEG, PNG, or GIF)', 'danger');
          return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
          showAlert('Please select an image smaller than 5MB', 'danger');
          return;
        }
        
        // Display loading
        const hideLoading = showLoading('Uploading image...');
        
        // Create form data and upload
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/upload', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          hideLoading();
          
          if (data.success) {
            // Show editor and update preview
            if (uploadContainer) uploadContainer.style.display = 'none';
            if (editorContainer) editorContainer.style.display = 'block';
            
            // Update preview image
            previewImg.src = data.url;
            currentImage = data.url;
            
            // Reset active tool
            toolButtons.forEach(btn => btn.classList.remove('active'));
            
            // Clear controls
            controlsContainer.innerHTML = '';
            
            // Clear undo/redo stacks
            onImageLoaded(data.url);
          } else {
            showAlert(data.error || 'Error uploading image', 'danger');
          }
        })
        .catch(error => {
          hideLoading();
          showAlert('Error uploading image: ' + error.message, 'danger');
        });
      }
    });
  }
  
  // Handle tool button clicks
  toolButtons.forEach(button => {
    button.addEventListener('click', function() {
      if (isProcessing || !currentImage) return;
      
      // Remove active class from all buttons
      toolButtons.forEach(btn => btn.classList.remove('active'));
      
      // Add active class to clicked button
      this.classList.add('active');
      
      // Get tool type from data attribute
      const tool = this.dataset.tool;
      
      // Show appropriate controls based on tool
      showToolControls(tool);
    });
  });
  
  // Reset button
  if (resetButton) {
    resetButton.addEventListener('click', function() {
      if (isProcessing || !currentImage) return;
      
      const hideLoading = showLoading('Resetting image...');
      
      fetch('/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        hideLoading();
        
        if (data.success) {
          previewImg.src = data.url;
          onImageLoaded(data.url); // <-- clear undo/redo
          
          // Reset active tool
          toolButtons.forEach(btn => btn.classList.remove('active'));
          
          // Clear controls
          controlsContainer.innerHTML = '';
          
        } else {
          showAlert(data.error || 'Error resetting image', 'danger');
        }
      })
      .catch(error => {
        hideLoading();
        showAlert('Error resetting image: ' + error.message, 'danger');
      });
    });
  }
  
  // Download button
  if (downloadButton) {
    downloadButton.addEventListener('click', function() {
      if (!currentImage) return;
      
      // Create a temporary link to download the image
      const a = document.createElement('a');
      a.href = currentImage;
      a.download = 'edited-image' + currentImage.split('.').pop();
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
    });
  }
  
  // Utility: update undo/redo button state
  function updateUndoRedoButtons() {
    if (undoButton) undoButton.disabled = undoStack.length === 0;
    if (redoButton) redoButton.disabled = redoStack.length === 0;
  }

  // Utility: push current image to undo stack
  function pushUndo() {
    if (currentImage) {
      undoStack.push(currentImage);
      // Limit stack size if needed
      if (undoStack.length > 20) undoStack.shift();
      redoStack = [];
      updateUndoRedoButtons();
    }
  }

  // Undo action
  function undo() {
    if (undoStack.length === 0) return;
    redoStack.push(currentImage);
    currentImage = undoStack.pop();
    previewImg.src = currentImage;
    updateUndoRedoButtons();
    // Optionally clear controls
    controlsContainer.innerHTML = '';
  }

  // Redo action
  function redo() {
    if (redoStack.length === 0) return;
    undoStack.push(currentImage);
    currentImage = redoStack.pop();
    previewImg.src = currentImage;
    updateUndoRedoButtons();
    controlsContainer.innerHTML = '';
  }

  // Wire up Undo/Redo buttons
  if (undoButton) {
    undoButton.addEventListener('click', function() {
      if (isProcessing) return;
      undo();
    });
  }
  if (redoButton) {
    redoButton.addEventListener('click', function() {
      if (isProcessing) return;
      redo();
    });
  }

  // Function to show tool-specific controls
  function showToolControls(tool) {
    controlsContainer.innerHTML = '';
    
    switch (tool) {
      case 'remove-background':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Background Color</label>
            <div class="color-picker">
              <div class="color-option active" style="background: transparent" data-color="transparent" title="Transparent"></div>
              <div class="color-option" style="background: #ffffff" data-color="#ffffff" title="White"></div>
              <div class="color-option" style="background: #000000" data-color="#000000" title="Black"></div>
              <div class="color-option" style="background: #ff0000" data-color="#ff0000" title="Red"></div>
              <div class="color-option" style="background: #00ff00" data-color="#00ff00" title="Green"></div>
              <div class="color-option" style="background: #0000ff" data-color="#0000ff" title="Blue"></div>
              <div class="color-option color-custom" style="background: linear-gradient(to right, red, blue)" title="Custom Color">
                <input type="color" id="custom-color">
              </div>
            </div>
          </div>
          <button id="apply-remove-bg" class="btn btn-primary mt-3">Remove Background</button>
        `;
        
        // Set up color options
        document.querySelectorAll('.color-option').forEach(option => {
          option.addEventListener('click', function() {
            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
          });
        });
        
        // Custom color picker
        const customColorInput = document.getElementById('custom-color');
        if (customColorInput) {
          customColorInput.addEventListener('input', function() {
            document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('active'));
            this.parentElement.classList.add('active');
          });
        }
        
        // Apply button
        const applyButton = document.getElementById('apply-remove-bg');
        if (applyButton) {
          applyButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            // Get selected color
            let color = document.querySelector('.color-option.active').dataset.color;
            
            // If it's the custom color, get the input value
            if (!color) {
              color = document.getElementById('custom-color').value;
            }
            
            // Process the image
            processImage('remove_background', { color: color });
          });
        }
        break;
        
      case 'enhance':
        controlsContainer.innerHTML = `
          <div class="alert alert-info mb-3">
            This will automatically enhance your image by adjusting brightness, contrast, saturation, and sharpness.
          </div>
          <button id="apply-enhance" class="btn btn-primary">Enhance Image</button>
        `;
        
        // Apply button
        const enhanceButton = document.getElementById('apply-enhance');
        if (enhanceButton) {
          enhanceButton.addEventListener('click', function() {
            if (isProcessing) return;
            processImage('enhance');
          });
        }
        break;
        
      case 'resize':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Width (px)</label>
            <input type="number" id="resize-width" class="form-control mb-2" min="1" max="5000">
          </div>
          <div class="control-group">
            <label class="control-label">Height (px)</label>
            <input type="number" id="resize-height" class="form-control mb-3" min="1" max="5000">
          </div>
          <button id="apply-resize" class="btn btn-primary">Resize Image</button>
        `;
        
        // Get original dimensions
        const img = new Image();
        img.src = currentImage;
        img.onload = function() {
          document.getElementById('resize-width').value = this.width;
          document.getElementById('resize-height').value = this.height;
        };
        
        // Apply button
        const resizeButton = document.getElementById('apply-resize');
        if (resizeButton) {
          resizeButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const width = document.getElementById('resize-width').value;
            const height = document.getElementById('resize-height').value;
            
            if (!width || !height) {
              showAlert('Please enter both width and height', 'warning');
              return;
            }
            
            processImage('resize', { width: width, height: height });
          });
        }
        break;
        
      case 'rotate':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Angle (degrees)</label>
            <input type="range" id="rotate-angle" class="control-slider" min="0" max="360" value="90" step="1">
            <div class="d-flex justify-content-between">
              <span>0°</span>
              <span id="angle-value">90°</span>
              <span>360°</span>
            </div>
          </div>
          <div class="d-flex justify-content-between mt-3">
            <button data-angle="90" class="btn btn-secondary rotate-preset">90°</button>
            <button data-angle="180" class="btn btn-secondary rotate-preset">180°</button>
            <button data-angle="270" class="btn btn-secondary rotate-preset">270°</button>
          </div>
          <button id="apply-rotate" class="btn btn-primary mt-3">Rotate Image</button>
        `;
        
        // Angle slider
        const angleSlider = document.getElementById('rotate-angle');
        const angleValue = document.getElementById('angle-value');
        
        if (angleSlider && angleValue) {
          angleSlider.addEventListener('input', function() {
            angleValue.textContent = this.value + '°';
          });
        }
        
        // Preset buttons
        document.querySelectorAll('.rotate-preset').forEach(button => {
          button.addEventListener('click', function() {
            if (angleSlider && angleValue) {
              angleSlider.value = this.dataset.angle;
              angleValue.textContent = this.dataset.angle + '°';
            }
          });
        });
        
        // Apply button
        const rotateButton = document.getElementById('apply-rotate');
        if (rotateButton) {
          rotateButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const angle = document.getElementById('rotate-angle').value;
            processImage('rotate', { angle: angle });
          });
        }
        break;
        
      case 'flip':
        controlsContainer.innerHTML = `
          <div class="control-group text-center">
            <button id="flip-horizontal" class="btn btn-secondary">Flip Horizontal</button>
            <button id="flip-vertical" class="btn btn-secondary mt-2">Flip Vertical</button>
          </div>
        `;
        
        // Horizontal flip button
        const flipHButton = document.getElementById('flip-horizontal');
        if (flipHButton) {
          flipHButton.addEventListener('click', function() {
            if (isProcessing) return;
            processImage('flip', { direction: 'horizontal' });
          });
        }
        
        // Vertical flip button
        const flipVButton = document.getElementById('flip-vertical');
        if (flipVButton) {
          flipVButton.addEventListener('click', function() {
            if (isProcessing) return;
            processImage('flip', { direction: 'vertical' });
          });
        }
        break;
        
      case 'brightness':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Brightness</label>
            <input type="range" id="brightness-slider" class="control-slider" min="0" max="2" value="1" step="0.05">
            <div class="d-flex justify-content-between">
              <span>Dark</span>
              <span id="brightness-value">1.00</span>
              <span>Bright</span>
            </div>
          </div>
          <button id="apply-brightness" class="btn btn-primary mt-3">Apply</button>
        `;
        
        // Brightness slider
        const brightnessSlider = document.getElementById('brightness-slider');
        const brightnessValue = document.getElementById('brightness-value');
        
        if (brightnessSlider && brightnessValue) {
          brightnessSlider.addEventListener('input', function() {
            brightnessValue.textContent = parseFloat(this.value).toFixed(2);
          });
        }
        
        // Apply button
        const brightnessButton = document.getElementById('apply-brightness');
        if (brightnessButton) {
          brightnessButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const factor = document.getElementById('brightness-slider').value;
            processImage('brightness', { factor: factor });
          });
        }
        break;
        
      case 'contrast':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Contrast</label>
            <input type="range" id="contrast-slider" class="control-slider" min="0" max="2" value="1" step="0.05">
            <div class="d-flex justify-content-between">
              <span>Low</span>
              <span id="contrast-value">1.00</span>
              <span>High</span>
            </div>
          </div>
          <button id="apply-contrast" class="btn btn-primary mt-3">Apply</button>
        `;
        
        // Contrast slider
        const contrastSlider = document.getElementById('contrast-slider');
        const contrastValue = document.getElementById('contrast-value');
        
        if (contrastSlider && contrastValue) {
          contrastSlider.addEventListener('input', function() {
            contrastValue.textContent = parseFloat(this.value).toFixed(2);
          });
        }
        
        // Apply button
        const contrastButton = document.getElementById('apply-contrast');
        if (contrastButton) {
          contrastButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const factor = document.getElementById('contrast-slider').value;
            processImage('contrast', { factor: factor });
          });
        }
        break;
        
      case 'saturation':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Saturation</label>
            <input type="range" id="saturation-slider" class="control-slider" min="0" max="2" value="1" step="0.05">
            <div class="d-flex justify-content-between">
              <span>B&W</span>
              <span id="saturation-value">1.00</span>
              <span>Vivid</span>
            </div>
          </div>
          <button id="apply-saturation" class="btn btn-primary mt-3">Apply</button>
        `;
        
        // Saturation slider
        const saturationSlider = document.getElementById('saturation-slider');
        const saturationValue = document.getElementById('saturation-value');
        
        if (saturationSlider && saturationValue) {
          saturationSlider.addEventListener('input', function() {
            saturationValue.textContent = parseFloat(this.value).toFixed(2);
          });
        }
        
        // Apply button
        const saturationButton = document.getElementById('apply-saturation');
        if (saturationButton) {
          saturationButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const factor = document.getElementById('saturation-slider').value;
            processImage('saturation', { factor: factor });
          });
        }
        break;
        
      case 'hue':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Hue Shift</label>
            <input type="range" id="hue-slider" class="control-slider" min="0" max="360" value="0" step="1">
            <div class="d-flex justify-content-between">
              <span>0°</span>
              <span id="hue-value">0°</span>
              <span>360°</span>
            </div>
          </div>
          <button id="apply-hue" class="btn btn-primary mt-3">Apply</button>
        `;
        
        // Hue slider
        const hueSlider = document.getElementById('hue-slider');
        const hueValue = document.getElementById('hue-value');
        
        if (hueSlider && hueValue) {
          hueSlider.addEventListener('input', function() {
            hueValue.textContent = this.value + '°';
          });
        }
        
        // Apply button
        const hueButton = document.getElementById('apply-hue');
        if (hueButton) {
          hueButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const factor = document.getElementById('hue-slider').value;
            processImage('hue', { factor: factor });
          });
        }
        break;
        
      case 'filter':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Filter Type</label>
            <div class="filter-options mt-2">
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="none">None</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="sepia">Sepia</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="vintage">Vintage</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="cool">Cool</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="warm">Warm</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="grayscale">Grayscale</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="high_contrast">High Contrast</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="nostalgia">Nostalgia</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="dramatic">Dramatic</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="cinema">Cinema</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="chrome">Chrome</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="fade">Fade</button>
              <button class="btn btn-secondary mr-2 mb-2 filter-option" data-filter="invert">Invert</button>
            </div>
          </div>
          <div class="control-group mt-3" id="filter-intensity-control" style="display: none;">
            <label class="control-label">Filter Intensity</label>
            <input type="range" id="filter-intensity" class="control-slider" min="0" max="100" value="100" step="1">
            <div class="d-flex justify-content-between">
              <span>Subtle</span>
              <span id="intensity-value">100%</span>
              <span>Strong</span>
            </div>
          </div>
        `;
        
        // Filter option buttons
        document.querySelectorAll('.filter-option').forEach(button => {
          button.addEventListener('click', function() {
            if (isProcessing) return;
            
            const filter = this.dataset.filter;
            const intensityControl = document.getElementById('filter-intensity-control');
            
            // Show/hide intensity slider based on filter selection
            if (filter === 'none') {
              intensityControl.style.display = 'none';
              // Reset to original instead of applying a filter
              fetch('/reset', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                }
              })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  previewImg.src = data.url;
                  onImageLoaded(data.url);
                } else {
                  showAlert(data.error || 'Error resetting image', 'danger');
                }
              });
            } else {
              intensityControl.style.display = 'block';
              const intensity = document.getElementById('filter-intensity').value;
              processImage('filter', { type: filter, intensity: intensity });
            }
            
            // Update active state
            document.querySelectorAll('.filter-option').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
          });
        });
        
        // Intensity slider
        const intensitySlider = document.getElementById('filter-intensity');
        const intensityValue = document.getElementById('intensity-value');
        
        if (intensitySlider && intensityValue) {
          let isAdjusting = false;  // Prevent multiple simultaneous adjustments
          
          intensitySlider.addEventListener('input', function() {
            if (isAdjusting) return;
            isAdjusting = true;
            
            intensityValue.textContent = this.value + '%';
            
            // Apply filter with new intensity if a filter is selected
            const activeFilter = document.querySelector('.filter-option.active');
            if (activeFilter && activeFilter.dataset.filter !== 'none') {
              // First reset to original
              fetch('/reset', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                }
              })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  // Then apply new filter with current intensity
                  processImage('filter', { 
                    type: activeFilter.dataset.filter, 
                    intensity: intensitySlider.value 
                  });
                }
                isAdjusting = false;
              })
              .catch(() => {
                isAdjusting = false;
              });
            } else {
              isAdjusting = false;
            }
          });
        }
        break;
        
      case 'bw':
        controlsContainer.innerHTML = `
          <div class="alert alert-info mb-3">
            Convert your image to black and white.
          </div>
          <button id="apply-bw" class="btn btn-primary">Convert to B&W</button>
        `;
        
        // Apply button
        const bwButton = document.getElementById('apply-bw');
        if (bwButton) {
          bwButton.addEventListener('click', function() {
            if (isProcessing) return;
            processImage('bw');
          });
        }
        break;
        
      case 'blur':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Blur Amount</label>
            <input type="range" id="blur-slider" class="control-slider" min="0" max="20" value="5" step="0.5">
            <div class="d-flex justify-content-between">
              <span>None</span>
              <span id="blur-value">5.0</span>
              <span>Max</span>
            </div>
          </div>
          <button id="apply-blur" class="btn btn-primary mt-3">Apply</button>
        `;
        
        // Blur slider
        const blurSlider = document.getElementById('blur-slider');
        const blurValue = document.getElementById('blur-value');
        
        if (blurSlider && blurValue) {
          blurSlider.addEventListener('input', function() {
            blurValue.textContent = parseFloat(this.value).toFixed(1);
          });
        }
        
        // Apply button
        const blurButton = document.getElementById('apply-blur');
        if (blurButton) {
          blurButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const amount = document.getElementById('blur-slider').value;
            processImage('blur', { amount: amount });
          });
        }
        break;
        
      case 'sharpen':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Sharpen Amount</label>
            <input type="range" id="sharpen-slider" class="control-slider" min="0" max="5" value="1.5" step="0.1">
            <div class="d-flex justify-content-between">
              <span>None</span>
              <span id="sharpen-value">1.5</span>
              <span>Max</span>
            </div>
          </div>
          <button id="apply-sharpen" class="btn btn-primary mt-3">Apply</button>
        `;
        
        // Sharpen slider
        const sharpenSlider = document.getElementById('sharpen-slider');
        const sharpenValue = document.getElementById('sharpen-value');
        
        if (sharpenSlider && sharpenValue) {
          sharpenSlider.addEventListener('input', function() {
            sharpenValue.textContent = parseFloat(this.value).toFixed(1);
          });
        }
        
        // Apply button
        const sharpenButton = document.getElementById('apply-sharpen');
        if (sharpenButton) {
          sharpenButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const amount = document.getElementById('sharpen-slider').value;
            processImage('sharpen', { amount: amount });
          });
        }
        break;
        
      case 'compress':
        controlsContainer.innerHTML = `
          <div class="control-group">
            <label class="control-label">Quality</label>
            <input type="range" id="quality-slider" class="control-slider" min="1" max="100" value="85" step="1">
            <div class="d-flex justify-content-between">
              <span>Low</span>
              <span id="quality-value">85%</span>
              <span>High</span>
            </div>
          </div>
          <div class="alert alert-info mt-3">
            Lower quality results in smaller file size.
          </div>
          <button id="apply-compress" class="btn btn-primary mt-3">Compress Image</button>
        `;
        
        // Quality slider
        const qualitySlider = document.getElementById('quality-slider');
        const qualityValue = document.getElementById('quality-value');
        
        if (qualitySlider && qualityValue) {
          qualitySlider.addEventListener('input', function() {
            qualityValue.textContent = this.value + '%';
          });
        }
        
        // Apply button
        const compressButton = document.getElementById('apply-compress');
        if (compressButton) {
          compressButton.addEventListener('click', function() {
            if (isProcessing) return;
            
            const quality = document.getElementById('quality-slider').value;
            processImage('compress', { quality: quality });
          });
        }
        break;
        
      default:
        controlsContainer.innerHTML = '<div class="alert alert-info">Select a tool from the left panel</div>';
        break;
    }
  }
  
  // Process image with selected operation
  function processImage(operation, params = {}) {
    if (isProcessing || !currentImage) return;
    
    pushUndo(); // Save state before processing
    isProcessing = true;
    const hideLoading = showLoading('Processing image...');
    
    fetch('/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        operation: operation,
        params: params
      })
    })
    .then(response => response.json())
    .then(data => {
      hideLoading();
      isProcessing = false;
      
      if (data.success) {
        // Update preview with new image
        previewImg.src = data.url + '?t=' + new Date().getTime(); // Add timestamp to prevent caching
        currentImage = data.url;
        
        updateUndoRedoButtons();
      } else {
        showAlert(data.error || 'Error processing image', 'danger');
      }
    })
    .catch(error => {
      hideLoading();
      isProcessing = false;
      showAlert('Error processing image: ' + error.message, 'danger');
    });
  }

  // After image upload or reset, clear stacks
  function onImageLoaded(newUrl) {
    currentImage = newUrl;
    undoStack = [];
    redoStack = [];
    updateUndoRedoButtons();
  }
});
