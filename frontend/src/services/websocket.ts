/**
 * WebSocket service for real-time communication with the backend
 */

type MessageCallback = (data: any) => void;
type ConnectionCallback = () => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private messageHandlers: Map<string, Set<MessageCallback>> = new Map();
  private connectionHandlers: {
    onOpen: Set<ConnectionCallback>,
    onClose: Set<ConnectionCallback>,
    onError: Set<ConnectionCallback>,
  } = {
    onOpen: new Set(),
    onClose: new Set(),
    onError: new Set(),
  };

  /**
   * Connect to a websocket endpoint
   * @param taskId The task ID to connect to
   */
  connect(taskId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Close any existing connection
        this.disconnect();

        // Create a new WebSocket connection
        // Connect directly to the backend server
        const wsUrl = `ws://127.0.0.1:8000/ws/${taskId}`;
        
        console.log(`Connecting to WebSocket at ${wsUrl}`);
        this.socket = new WebSocket(wsUrl);

        // Setup event handlers
        this.socket.onopen = () => {
          console.log(`WebSocket connected to task ${taskId}`);
          this.connectionHandlers.onOpen.forEach(handler => handler());
          resolve();
        };

        this.socket.onclose = (event) => {
          console.log(`WebSocket disconnected from task ${taskId}`, event.code, event.reason);
          this.connectionHandlers.onClose.forEach(handler => handler());
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.connectionHandlers.onError.forEach(handler => handler());
          reject(error);
        };

        this.socket.onmessage = (event) => {
          try {
            console.log('WebSocket message received:', event.data);
            const message = JSON.parse(event.data);
            const messageType = message.type;
            
            // Call handlers for this message type
            if (this.messageHandlers.has(messageType)) {
              this.messageHandlers.get(messageType)?.forEach(handler => {
                handler(message.data);
              });
            }
            
            // Call handlers for "all" message types
            if (this.messageHandlers.has('all')) {
              this.messageHandlers.get('all')?.forEach(handler => {
                handler(message);
              });
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
      } catch (error) {
        console.error('Error connecting to WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the websocket
   */
  disconnect(): void {
    if (this.socket) {
      console.log('Disconnecting WebSocket');
      this.socket.close();
      this.socket = null;
    }
  }

  /**
   * Send a message through the websocket
   */
  send(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('Sending WebSocket message:', message);
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  /**
   * Register a handler for a specific message type
   */
  onMessage(type: string, callback: MessageCallback): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    
    this.messageHandlers.get(type)?.add(callback);
    console.log(`Registered handler for message type: ${type}`);
    
    // Return a function to remove this handler
    return () => {
      this.messageHandlers.get(type)?.delete(callback);
    };
  }

  /**
   * Register a handler for connection open events
   */
  onOpen(callback: ConnectionCallback): () => void {
    this.connectionHandlers.onOpen.add(callback);
    return () => this.connectionHandlers.onOpen.delete(callback);
  }

  /**
   * Register a handler for connection close events
   */
  onClose(callback: ConnectionCallback): () => void {
    this.connectionHandlers.onClose.add(callback);
    return () => this.connectionHandlers.onClose.delete(callback);
  }

  /**
   * Register a handler for connection error events
   */
  onError(callback: ConnectionCallback): () => void {
    this.connectionHandlers.onError.add(callback);
    return () => this.connectionHandlers.onError.delete(callback);
  }

  /**
   * Check if the websocket is connected
   */
  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export default websocketService; 