import { useRef, useState, useEffect } from 'react';
import './App.css';

function App() {
  const canvasRef = useRef(null);
  const contextRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState('pen'); // Track the tool (pen/eraser)

  // Setup canvas based on device's pixel ratio and screen size
  const setupCanvas = () => {
    const canvas = canvasRef.current;
    const pixelRatio = window.devicePixelRatio || 1;

    // Set canvas size based on window size and device pixel ratio
    const width = window.innerWidth;
    const height = window.innerHeight;

    canvas.width = width * pixelRatio;
    canvas.height = height * pixelRatio;
    canvas.style.width = `${width - 100}px`;
    canvas.style.height = `${height - 100}px`;

    const context = canvas.getContext('2d');
    context.scale(pixelRatio, pixelRatio); // Scale canvas for high DPI displays
    context.lineCap = 'round';
    context.strokeStyle = 'black';
    context.lineWidth = 5;
    contextRef.current = context;
  };

  useEffect(() => {
    setupCanvas(); // Initialize canvas when the component mounts

    // Redraw the canvas on window resize
    window.addEventListener('resize', setupCanvas);
    return () => window.removeEventListener('resize', setupCanvas);
  }, []);

  const startDrawing = ({ nativeEvent }) => {
    const { offsetX, offsetY } = nativeEvent;
    contextRef.current.beginPath();
    contextRef.current.moveTo(offsetX, offsetY);
    setIsDrawing(true);
  };

  const finishDrawing = () => {
    contextRef.current.closePath();
    setIsDrawing(false);
  };

  const draw = ({ nativeEvent }) => {
    if (!isDrawing) return;
    const { offsetX, offsetY } = nativeEvent;

    if (tool === 'pen') {
      contextRef.current.strokeStyle = 'black'; // Pen color
      contextRef.current.lineWidth = 5; // Pen width
    } else if (tool === 'eraser') {
      contextRef.current.strokeStyle = 'white'; // Eraser color
      contextRef.current.lineWidth = 20; // Eraser size
    }

    contextRef.current.lineTo(offsetX, offsetY);
    contextRef.current.stroke();
  };

  // Clear the canvas
  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const context = contextRef.current;
    context.clearRect(0, 0, canvas.width, canvas.height);
  };

  return (
    <div className="App">
      <div className="toolbar">
        <button
          className={`tool-button ${tool === 'pen' ? 'active' : ''}`}
          onClick={() => setTool('pen')}
        >
          Pen
        </button>
        <button
          className={`tool-button ${tool === 'eraser' ? 'active' : ''}`}
          onClick={() => setTool('eraser')}
        >
          Eraser
        </button>
        <button className="tool-button clear-button" onClick={clearCanvas}>
          Clear Canvas
        </button>
      </div>
      <canvas
        onMouseDown={startDrawing}
        onMouseUp={finishDrawing}
        onMouseMove={draw}
        onMouseLeave={finishDrawing}
        ref={canvasRef}
      />
    </div>
  );
}

export default App;
