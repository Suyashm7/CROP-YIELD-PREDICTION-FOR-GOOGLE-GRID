import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def visualize_model(model_params=None):
    st.subheader("🧠 Interactive BLSTM Model Architecture Visualization")
    
    # Check if data is already preprocessed and stored in session state
    if 'model_visualization_data' not in st.session_state:
        with st.spinner("Initializing model visualization... Please wait"):
            try:
                # Store default parameters in session state
                st.session_state['model_visualization_data'] = {
                    'hidden_units': 64,
                    'dropout_size': 0.2,
                    'input_timesteps': 12,
                    'input_features': 8,
                    'n_out': 1,
                    'animate': True
                }
                
            except Exception as e:
                st.error(f"Error in visualization initialization: {str(e)}")
                return
    
    # View selector buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("3D Architecture View"):
            st.session_state['model_view'] = '3d_model'
    with col2:
        if st.button("Layer Information View"):
            st.session_state['model_view'] = 'layer_info'

    # Set default view if not already set
    if 'model_view' not in st.session_state:
        st.session_state['model_view'] = '3d_model'

    # Parameter controls
    st.sidebar.header("Model Parameters")
    hidden_units = st.sidebar.slider("Hidden Units", min_value=8, max_value=128, value=st.session_state['model_visualization_data']['hidden_units'], step=8)
    dropout_size = st.sidebar.slider("Dropout Rate", min_value=0.0, max_value=0.5, value=st.session_state['model_visualization_data']['dropout_size'], step=0.05)
    input_timesteps = st.sidebar.slider("Input Timesteps", min_value=5, max_value=30, value=st.session_state['model_visualization_data']['input_timesteps'], step=1)
    input_features = st.sidebar.slider("Input Features", min_value=1, max_value=20, value=st.session_state['model_visualization_data']['input_features'], step=1)
    n_out = st.sidebar.slider("Output Units", min_value=1, max_value=10, value=st.session_state['model_visualization_data']['n_out'], step=1)
    
    # Animation controls
    animate = st.sidebar.checkbox("Animate Data Flow", value=st.session_state['model_visualization_data']['animate'])
    
    # Update session state
    st.session_state['model_visualization_data'] = {
        'hidden_units': hidden_units,
        'dropout_size': dropout_size,
        'input_timesteps': input_timesteps,
        'input_features': input_features,
        'n_out': n_out,
        'animate': animate
    }
    
    # Display the selected view using parameters
    if st.session_state['model_view'] == '3d_model':
        display_3d_model_view(st.session_state['model_visualization_data'])
    elif st.session_state['model_view'] == 'layer_info':
        display_layer_info_view(st.session_state['model_visualization_data'])


def display_3d_model_view(params):
    """Display 3D model architecture visualization"""
    
    # Define layers and nodes count
    layer_names = [
        "input", 
        "blstm1", 
        "dropout1", 
        "blstm2", 
        "dropout2", 
        "dense1", 
        "dense2", 
        "output"
    ]
    
    nodes_per_layer = [
        params['input_timesteps'] * params['input_features'],  # Input layer
        params['hidden_units'] * 2,  # BLSTM1 (bidirectional)
        params['hidden_units'] * 2,  # Dropout1 (same as BLSTM1)
        params['hidden_units'] * 2,  # BLSTM2 (bidirectional)
        params['hidden_units'] * 2,  # Dropout2 (same as BLSTM2)
        params['hidden_units'] * 2,  # Dense1
        params['hidden_units'],      # Dense2
        params['n_out']              # Output
    ]
    
    # Create 3D model visualization
    fig = create_model_visualization(layer_names, nodes_per_layer, params)
    
    # Display the figure
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation below the chart
    with st.expander("Model Architecture Explanation", expanded=False):
        st.write("""
        This 3D visualization represents a Bidirectional LSTM (BLSTM) neural network architecture for crop yield prediction.
        
        **Key Components:**
        - **Input Layer:** Processes time series data with multiple features (e.g., weather, soil conditions)
        - **BLSTM Layers:** Process sequences in both forward and backward directions to capture temporal dependencies
        - **Dropout Layers:** Prevent overfitting by randomly disabling neurons during training
        - **Dense Layers:** Extract and combine high-level features
        - **Output Layer:** Generates the final yield prediction
        
        **How to Use:**
        - Adjust parameters in the sidebar to see how they affect the model architecture
        - Toggle animation to visualize connections between layers
        - Rotate, zoom, and pan the 3D plot to explore from different angles
        """)


def display_layer_info_view(params):
    """Display detailed layer information"""
    st.subheader("BLSTM Model Layer Information")
    
    # Create a DataFrame with layer information
    layer_info = pd.DataFrame({
        "Layer": [
            "Input", 
            "Bidirectional LSTM 1", 
            "Dropout 1", 
            "Bidirectional LSTM 2", 
            "Dropout 2", 
            "Dense 1", 
            "Dense 2", 
            "Output"
        ],
        "Shape": [
            f"({params['input_timesteps']}, {params['input_features']})",
            f"({params['input_timesteps']}, {params['hidden_units']*2})",
            f"({params['input_timesteps']}, {params['hidden_units']*2})",
            f"({params['hidden_units']*2})",
            f"({params['hidden_units']*2})",
            f"({params['hidden_units']*2})",
            f"({params['hidden_units']})",
            f"({params['n_out']})"
        ],
        "Parameters": [
            "0",
            f"{4 * params['hidden_units'] * (params['input_features'] + params['hidden_units'] + 1)}",
            "0",
            f"{4 * params['hidden_units'] * (params['hidden_units']*2 + params['hidden_units'] + 1)}",
            "0",
            f"{params['hidden_units']*2 * params['hidden_units']*2 + params['hidden_units']*2}",
            f"{params['hidden_units']*2 * params['hidden_units'] + params['hidden_units']}",
            f"{params['hidden_units'] * params['n_out'] + params['n_out']}"
        ],
        "Description": [
            f"Input shape for time series data with {params['input_features']} features over {params['input_timesteps']} timesteps",
            "Processes sequences in both forward and backward directions with tanh activation",
            f"Randomly drops {params['dropout_size']*100}% of inputs to prevent overfitting",
            "Second bidirectional LSTM layer with tanh activation",
            f"Randomly drops {params['dropout_size']*100}% of inputs to prevent overfitting",
            "Fully connected layer with ReLU activation",
            "Fully connected layer with ReLU activation",
            "Output layer for yield prediction"
        ]
    })
    
    # Display the table
    st.table(layer_info)
    
    # Show parameter summary
    total_params = sum([int(p.replace(',', '')) if p.replace(',', '').isdigit() else 0 for p in layer_info["Parameters"]])
    st.info(f"Total model parameters: {total_params:,}")
    
    # Show model code
    st.subheader("BLSTM Model Code")
    model_code = f"""
# Define the BLSTM model for crop yield prediction
def BLstm_model():
    input1 = tf.keras.layers.Input(shape=({params['input_timesteps']}, {params['input_features']}))
    blstm_1 = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM({params['hidden_units']}, activation='tanh', return_sequences=True, name='blstm1')
    )(input1)
    drop1 = tf.keras.layers.Dropout({params['dropout_size']})(blstm_1)

    blstm_2 = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM({params['hidden_units']}, activation='tanh', return_sequences=False, name='blstm2')
    )(drop1)
    drop2 = tf.keras.layers.Dropout({params['dropout_size']})(blstm_2)

    dense_1 = tf.keras.layers.Dense({params['hidden_units'] * 2}, activation='relu')(drop2)
    dense_2 = tf.keras.layers.Dense({params['hidden_units']}, activation='relu')(dense_1)
    output = tf.keras.layers.Dense({params['n_out']})(dense_2)

    model = tf.keras.Model(inputs=input1, outputs=output)
    optimizer = tf.keras.optimizers.Nadam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    return model
    """
    st.code(model_code, language="python")
    
    # Plot layer sizes visualization
    layer_names = ["Input", "BLSTM 1", "BLSTM 2", "Dense 1", "Dense 2", "Output"]
    layer_sizes = [
        params['input_timesteps'] * params['input_features'],
        params['hidden_units'] * 2,
        params['hidden_units'] * 2,
        params['hidden_units'] * 2,
        params['hidden_units'],
        params['n_out']
    ]
    
    # Create a horizontal bar chart of layer sizes
    fig = px.bar(
        x=layer_sizes,
        y=layer_names,
        orientation='h',
        title="Number of Units per Layer",
        labels={'x': 'Number of Units', 'y': 'Layer'},
        color=layer_sizes,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_model_visualization(layer_names, nodes_per_layer, params):
    """Create 3D model visualization - horizontal orientation"""
    # Define dimensions
    width, height, depth = 1.0, 1.0, 2.0
    
    total_layers = len(layer_names)
    
    # Create points for each layer
    layer_points = []
    for i in range(total_layers):
        points = create_layer_points_horizontal(i, total_layers, width, height, depth, nodes_per_layer[i], layer_names)
        layer_points.append(points)
    
    # Create the figure
    fig = go.Figure()
    
    # Add nodes for each layer
    colors = [
        'rgba(31, 119, 180, 0.8)',  # Input
        'rgba(255, 127, 14, 0.8)',  # BLSTM1
        'rgba(44, 160, 44, 0.8)',   # Dropout1
        'rgba(214, 39, 40, 0.8)',   # BLSTM2
        'rgba(148, 103, 189, 0.8)', # Dropout2
        'rgba(140, 86, 75, 0.8)',   # Dense1
        'rgba(227, 119, 194, 0.8)', # Dense2
        'rgba(127, 127, 127, 0.8)'  # Output
    ]
    
    # Add edges between layers
    for i in range(total_layers - 1):
        source_points = layer_points[i]
        target_points = layer_points[i + 1]
        
        # Add source layer nodes
        fig.add_trace(go.Scatter3d(
            x=source_points[:, 0],
            y=source_points[:, 1],
            z=source_points[:, 2],
            mode='markers',
            marker=dict(
                size=8,
                color=colors[i],
            ),
            name=layer_names[i],
            hoverinfo="name+text",
            hovertext=[f"Node {j}" for j in range(len(source_points))]
        ))
        
        # For visualization clarity, only show connections between specific layers when needed
        if params['animate'] and i < 7:  # Don't draw all connections to avoid visual clutter
            # Calculate the maximum number of connections to show
            max_connections = min(50, len(source_points) * len(target_points))
            
            connections_shown = 0
            
            # Connect a subset of nodes to avoid visual clutter
            for s_idx in range(0, len(source_points), max(1, len(source_points) // 5)):
                for t_idx in range(0, len(target_points), max(1, len(target_points) // 5)):
                    if connections_shown >= max_connections:
                        break
                        
                    s = source_points[s_idx]
                    t = target_points[t_idx]
                    
                    fig.add_trace(go.Scatter3d(
                        x=[s[0], t[0]],
                        y=[s[1], t[1]],
                        z=[s[2], t[2]],
                        mode='lines',
                        line=dict(color='rgba(100, 100, 100, 0.2)', width=1),
                        showlegend=False,
                        hoverinfo='none'
                    ))
                    connections_shown += 1
    
    # Add the last layer nodes
    fig.add_trace(go.Scatter3d(
        x=layer_points[-1][:, 0],
        y=layer_points[-1][:, 1],
        z=layer_points[-1][:, 2],
        mode='markers',
        marker=dict(
            size=8,
            color=colors[-1],
        ),
        name=layer_names[-1],
        hoverinfo="name+text",
        hovertext=[f"Output {j}" for j in range(len(layer_points[-1]))]
    ))
    
    # Create text annotations for each layer
    for i, layer_name in enumerate(layer_names):
        x_pos = i / (total_layers - 1) * depth - depth/2
        
        # Clean up the layer names
        display_name = layer_name
        if "blstm" in layer_name:
            display_name = f"Bidirectional LSTM ({params['hidden_units']} units)"
        elif "dropout" in layer_name:
            display_name = f"Dropout (rate={params['dropout_size']})"
        elif "dense" in display_name:
            units = params['hidden_units'] * 2 if "1" in layer_name else params['hidden_units']
            display_name = f"Dense ({units} units)"
        elif layer_name == "input":
            display_name = f"Input ({params['input_timesteps']}×{params['input_features']})"
        elif layer_name == "output":
            display_name = f"Output ({params['n_out']} units)"
        
        # Add text annotation below each layer
        fig.add_trace(go.Scatter3d(
            x=[x_pos],
            y=[-0.8],
            z=[0],
            mode='text',
            text=[display_name],
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title="BLSTM Neural Network Architecture",
        scene=dict(
            xaxis=dict(title="Layer", showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(title="", showticklabels=False, showgrid=False, zeroline=False),
            zaxis=dict(title="", showticklabels=False, showgrid=False, zeroline=False),
            aspectmode='manual',
            aspectratio=dict(x=2, y=1, z=1)
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=600
    )
    
    # Add camera position for horizontal view
    fig.update_layout(
        scene_camera=dict(
            eye=dict(x=0.1, y=2.5, z=0.1)
        )
    )
    
    return fig


def create_layer_points_horizontal(layer_idx, total_layers, width, height, depth, n_nodes, layer_names):
    """Create 3D points for a layer - horizontal orientation"""
    # In horizontal layout, x is the depth dimension (represents layer position)
    x = layer_idx / (total_layers - 1) * depth - depth/2
    
    points = []
    for i in range(n_nodes):
        # Limit the number of visible nodes for better visualization
        if n_nodes > 50 and i % (n_nodes // 25 + 1) != 0:
            continue
            
        y = (i / (n_nodes - 1 if n_nodes > 1 else 1)) * height - height/2
        
        # For LSTM layers, create forward and backward parts (now vertically separated)
        if "blstm" in layer_names[layer_idx]:
            # Forward cells (top)
            z_forward = width/4
            points.append([x, y, z_forward])
            
            # Backward cells (bottom)
            z_backward = -width/4
            points.append([x, y, z_backward])
        else:
            # Regular nodes are centered
            points.append([x, y, 0])
            
    return np.array(points)


# Add a reset button function to clear cached data if needed
def reset_model_visualization_cache():
    if st.sidebar.button("Reset Model Visualization Cache"):
        if 'model_visualization_data' in st.session_state:
            del st.session_state['model_visualization_data']
        if 'model_view' in st.session_state:
            del st.session_state['model_view']
        st.experimental_rerun()
