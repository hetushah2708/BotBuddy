var recLength = 0,
  recBuffers = [],
  sampleRate = 44100,
  numChannels = 1;

this.onmessage = function(e) {
  switch (e.data.command) {
    case 'init':
      init(e.data.config);
      break;
    case 'record':
      record(e.data.buffer);
      break;
    case 'exportWAV':
      exportWAV(e.data.type);
      break;
    case 'clear':
      clear();
      break;
  }
};

function init(config) {
  sampleRate = config.sampleRate || 44100;
  numChannels = config.numChannels || 1;
  initBuffers();
}

function record(buffer) {
  // Ensure we have buffers for all channels
  while (recBuffers.length < numChannels) {
    recBuffers.push([]);
  }

  for (var channel = 0; channel < numChannels; channel++) {
    // Make sure we have a buffer for this channel
    if (!recBuffers[channel]) {
      recBuffers[channel] = [];
    }
    // Add the new data to the channel buffer
    recBuffers[channel].push(new Float32Array(buffer[channel]));
  }
  recLength += buffer[0].length;
}

function exportWAV(type) {
  // Merge all channel buffers
  var channelBuffers = [];
  for (var channel = 0; channel < numChannels; channel++) {
    channelBuffers.push(mergeBuffers(recBuffers[channel], recLength));
  }

  // Interleave for stereo if needed
  var interleaved;
  if (numChannels === 2) {
    interleaved = interleavedBuffers(channelBuffers[0], channelBuffers[1]);
  } else {
    interleaved = channelBuffers[0];
  }

  // Create the WAV file
  var dataview = encodeWAV(interleaved);
  var audioBlob = new Blob([dataview], { type: type || 'audio/wav' });

  this.postMessage(audioBlob);
}

function clear() {
  recLength = 0;
  recBuffers = [];
}

function initBuffers() {
  recBuffers = [];
  for (var channel = 0; channel < numChannels; channel++) {
    recBuffers[channel] = [];
  }
}

function mergeBuffers(channelBuffers, recordingLength) {
  var result = new Float32Array(recordingLength);
  var offset = 0;
  for (var i = 0; i < channelBuffers.length; i++) {
    result.set(channelBuffers[i], offset);
    offset += channelBuffers[i].length;
  }
  return result;
}

function interleavedBuffers(leftChannel, rightChannel) {
  var length = leftChannel.length + rightChannel.length;
  var result = new Float32Array(length);

  var inputIndex = 0;
  for (var index = 0; index < length;) {
    result[index++] = leftChannel[inputIndex];
    result[index++] = rightChannel[inputIndex];
    inputIndex++;
  }
  return result;
}

function floatTo16BitPCM(output, offset, input) {
  for (var i = 0; i < input.length; i++, offset += 2) {
    var s = Math.max(-1, Math.min(1, input[i]));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
}

function writeString(view, offset, string) {
  for (var i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

function encodeWAV(samples) {
  // Check if we have samples to encode
  if (!samples || samples.length === 0) {
    throw new Error('No audio samples to encode');
  }

  var buffer = new ArrayBuffer(44 + samples.length * 2);
  var view = new DataView(buffer);

  /* RIFF identifier */
  writeString(view, 0, 'RIFF');
  /* RIFF chunk length */
  view.setUint32(4, 36 + samples.length * 2, true);
  /* RIFF type */
  writeString(view, 8, 'WAVE');
  /* format chunk identifier */
  writeString(view, 12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw) */
  view.setUint16(20, 1, true);
  /* channel count */
  view.setUint16(22, numChannels, true);
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sample rate * block align) */
  view.setUint32(28, sampleRate * numChannels * 2, true);
  /* block align (channel count * bytes per sample) */
  view.setUint16(32, numChannels * 2, true);
  /* bits per sample */
  view.setUint16(34, 16, true);
  /* data chunk identifier */
  writeString(view, 36, 'data');
  /* data chunk length */
  view.setUint32(40, samples.length * 2, true);

  floatTo16BitPCM(view, 44, samples);

  return view;
}