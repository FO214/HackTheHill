import { useRef, useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

const socket = io('http://localhost:9631'); // Replace with your Flask backend URL

function App() {
  const canvasRef = useRef(null);
  const contextRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState('pen'); // Track the tool (pen/eraser)
  const [penState, setPenState] = useState('up'); // State to track pen state from backend
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 }); // Track mouse position

  // Setup canvas based on device's pixel ratio and screen size
  const setupCanvas = () => {
    const canvas = canvasRef.current;
    const pixelRatio = window.devicePixelRatio || 1;

    const width = window.innerWidth * 0.9; // Make canvas 90% of window width
    const height = window.innerHeight * 0.75; // Make canvas 75% of window height

    canvas.width = width * pixelRatio;
    canvas.height = height * pixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const context = canvas.getContext('2d');
    context.scale(pixelRatio, pixelRatio); // Scale canvas for high DPI displays
    context.lineCap = 'round';
    context.strokeStyle = 'black';
    context.lineWidth = 5;
    contextRef.current = context;
  };

  useEffect(() => {
    setupCanvas(); // Initialize canvas when the component mounts

    window.addEventListener('resize', setupCanvas);
    return () => window.removeEventListener('resize', setupCanvas);
  }, []);

  useEffect(() => {
    // Listen for 'pen_state' event from the backend
    socket.on('pen_state', (data) => {
      console.log('Pen state:', data.state);
      setPenState(data.state); // Update the pen state in the frontend
    });

    // Listen for 'mouse_position' event from the backend
    socket.on('mouse_position', (data) => {
      console.log('Mouse position:', data);
      setMousePosition({ x: data.x, y: data.y }); // Update the mouse position in the frontend

      // If the pen is down, draw at the received mouse position
      if (penState === 'down') {
        drawAtPosition(data.x, data.y);
      }
    });

    return () => {
      socket.off('pen_state');
      socket.off('mouse_position');
    };
  }, [penState]);

  const startDrawing = ({ nativeEvent }) => {
    const { offsetX, offsetY } = nativeEvent;
    contextRef.current.beginPath();
    contextRef.current.moveTo(offsetX, offsetY);
    setIsDrawing(true);
    setPenState('down'); // Set pen state to down

    // Emit initial position to the backend
    socket.emit('mouse_position', { x: offsetX, y: offsetY });
  };

  const finishDrawing = () => {
    contextRef.current.closePath();
    setIsDrawing(false);
    setPenState('up'); // Set pen state to up
  };

  const drawAtPosition = (x, y) => {
    if (!isDrawing && penState === 'up') return; // Don't draw if the pen is up

    if (tool === 'pen') {
      contextRef.current.strokeStyle = 'black'; // Pen color
      contextRef.current.lineWidth = 5; // Pen width
    } else if (tool === 'eraser') {
      contextRef.current.strokeStyle = 'white'; // Eraser color
      contextRef.current.lineWidth = 20; // Eraser size
    }

    contextRef.current.lineTo(x, y);
    contextRef.current.stroke();
  };

  const draw = ({ nativeEvent }) => {
    const { offsetX, offsetY } = nativeEvent;
    // Update the mouse position without requiring the mouse to be down
    setMousePosition({ x: offsetX, y: offsetY });
    
    if (penState === 'down') {
      drawAtPosition(offsetX, offsetY);
      // Emit current mouse position to the backend
      socket.emit('mouse_position', { x: offsetX, y: offsetY });
    }
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const context = contextRef.current;
    context.clearRect(0, 0, canvas.width, canvas.height);
    setIsDrawing(false); // Set isDrawing to false to prevent re-drawing
    setMousePosition({ x: 0, y: 0 }); // Reset mouse position
    setPenState('up'); // Set pen state to up
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
      {/* Display pen state at the bottom */}
      <div className="pen-state">
        Pen is currently: <strong>{penState}</strong>
      </div>

      {/* Custom mouse cursor */}
      <div
        className="custom-cursor"
        style={{
          position: 'absolute',
          top: `${mousePosition.y + 100}px`, // Adjusted for half the cursor height
          left: `${mousePosition.x - 10 }px`, // Adjusted for half the cursor width
          width: '20px', // Cursor width
          height: '20px', // Cursor height
          backgroundColor: 'rgba(0, 0, 0, 0.5)', // Cursor color
          borderRadius: '50%',
          pointerEvents: 'none', // Prevent interfering with mouse events
        }}
      />

    </div>
  );
}

export default App;
