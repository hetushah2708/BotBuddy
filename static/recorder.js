(function(window){
    var WORKER_PATH = '/static/recorderWorker.js';
  
    var Recorder = function(source, cfg){
      var config = cfg || {};
      var bufferLen = config.bufferLen || 4096;
      this.context = source.context;
  
      // Use AudioWorkletNode if available, otherwise fall back to ScriptProcessorNode
      if (this.context.audioWorklet) {
        this.node = this.context.createGain();
      } else {
        this.node = this.context.createScriptProcessor(bufferLen, config.numChannels || 2, config.numChannels || 2);
      }
  
      var worker = new Worker(config.workerPath || WORKER_PATH);
  
      // Initialize worker
      worker.postMessage({
        command: 'init',
        config: {
          sampleRate: this.context.sampleRate,
          numChannels: config.numChannels || 1
        }
      });
  
      var recording = false,
        currCallback;
  
      // Handle audio processing
      if (this.node.onaudioprocess) {
        this.node.onaudioprocess = function(e) {
          if (!recording) return;
          worker.postMessage({
            command: 'record',
            buffer: [
              e.inputBuffer.getChannelData(0),
              config.numChannels > 1 ? e.inputBuffer.getChannelData(1) : null
            ].filter(Boolean) // Remove null values for mono
          });
        };
      } else {
        // For AudioWorkletNode, we'd need additional setup
        console.warn('AudioWorkletNode would require additional setup');
      }
  
      this.record = function(){
        recording = true;
      };
  
      this.stop = function(){
        recording = false;
      };
  
      this.clear = function(){
        worker.postMessage({ command: 'clear' });
      };
  
      this.exportWAV = function(cb, type){
        currCallback = cb || config.callback;
        if (!currCallback) throw new Error('Callback not set');
  
        console.log('Attempting to export WAV...');
        worker.postMessage({
          command: 'exportWAV',
          type: type
        });
      };
  
      worker.onmessage = function(e){
        var blob = e.data;
        currCallback(blob);
        console.log('WAV export complete, blob size:', blob.size);
      };
  
      // Connect the nodes
      source.connect(this.node);
      this.node.connect(this.context.destination);
  
      recorder && recorder.ondataavailable && (recorder.ondataavailable = function(e) {
        console.log('Audio data available:', e.data);
      });
    };
  
    window.Recorder = Recorder;
  })(window);
  