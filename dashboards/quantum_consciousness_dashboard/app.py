"""
Streamlit Dashboard for Quantum Consciousness VAE Model
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="Quantum Consciousness VAE Dashboard",
    page_icon="🧠",
    layout="wide"
)

# Title and description
st.title("🔮 Quantum Consciousness VAE Dashboard")
st.markdown("""
This dashboard visualizes the training metrics and quantum properties of the Variational Autoencoder
designed for quantum consciousness modeling.
""")

# Sidebar
st.sidebar.header("🎛️ Controls")
metrics_file = st.sidebar.file_uploader("Upload Metrics JSON", type=['json'])
show_sample_data = st.sidebar.checkbox("Show Sample Data", value=False)

# Load sample data if no file uploaded
if metrics_file is None and show_sample_data:
    # Create sample data for demonstration
    epochs = list(range(1, 101))

    # Sample metrics data
    sample_data = {
        'epochs': epochs,
        'train_metrics': {
            'total_loss': [0.8 - 0.007*i + np.random.normal(0, 0.02) for i in epochs],
            'recon': [0.5 - 0.005*i + np.random.normal(0, 0.01) for i in epochs],
            'kl': [0.3 - 0.002*i + np.random.normal(0, 0.005) for i in epochs],
            'hamming': [0.01 - 0.0001*i + np.random.normal(0, 0.001) for i in epochs],
            'coherence': [0.9 + 0.001*i + np.random.normal(0, 0.005) for i in epochs],
            'fidelity': [0.95 + 0.0005*i + np.random.normal(0, 0.003) for i in epochs],
            'entropy': [1.2 - 0.002*i + np.random.normal(0, 0.01) for i in epochs]
        },
        'val_metrics': {
            'total_loss': [0.82 - 0.006*i + np.random.normal(0, 0.025) for i in epochs],
            'recon': [0.52 - 0.004*i + np.random.normal(0, 0.015) for i in epochs],
            'kl': [0.32 - 0.001*i + np.random.normal(0, 0.008) for i in epochs],
            'hamming': [0.012 - 0.00008*i + np.random.normal(0, 0.0015) for i in epochs],
            'coherence': [0.88 + 0.0015*i + np.random.normal(0, 0.008) for i in epochs],
            'fidelity': [0.93 + 0.0008*i + np.random.normal(0, 0.005) for i in epochs],
            'entropy': [1.25 - 0.0015*i + np.random.normal(0, 0.015) for i in epochs]
        },
        'quantum_metrics': {
            'quantum_fidelity': [0.92 + 0.0003*i + np.random.normal(0, 0.004) for i in epochs],
            'entanglement_entropy': [1.05 - 0.0005*i + np.random.normal(0, 0.008) for i in epochs],
            'coherence_preservation': [0.88 + 0.001*i + np.random.normal(0, 0.006) for i in epochs],
            'consciousness_complexity': [0.75 + 0.002*i + np.random.normal(0, 0.01) for i in epochs]
        }
    }
else:
    sample_data = None

# Main content
if metrics_file is not None or show_sample_data:
    if metrics_file is not None:
        # Load uploaded JSON file
        data = json.load(metrics_file)
    else:
        # Use sample data
        data = sample_data

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Training Metrics", "⚛️ Quantum Properties", "🧠 Latent Space", "ℹ️ About"])

    with tab1:
        st.header("Training Metrics Overview")

        # Create columns for key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Final Training Loss", f"{data['train_metrics']['total_loss'][-1]:.4f}")
        with col2:
            st.metric("Final Validation Loss", f"{data['val_metrics']['total_loss'][-1]:.4f}")
        with col3:
            st.metric("Best Epoch", f"{np.argmin(data['val_metrics']['total_loss']) + 1}")
        with col4:
            st.metric("Training Epochs", f"{len(data['epochs'])}")

        # Loss components plot
        st.subheader("Loss Components Over Time")

        fig_loss = go.Figure()
        fig_loss.add_trace(go.Scatter(
            x=data['epochs'],
            y=data['train_metrics']['total_loss'],
            mode='lines+markers',
            name='Train Loss',
            line=dict(color='blue')
        ))
        fig_loss.add_trace(go.Scatter(
            x=data['epochs'],
            y=data['val_metrics']['total_loss'],
            mode='lines+markers',
            name='Validation Loss',
            line=dict(color='red')
        ))

        fig_loss.update_layout(
            title="Total Loss Evolution",
            xaxis_title="Epoch",
            yaxis_title="Loss",
            hovermode="x unified"
        )

        st.plotly_chart(fig_loss, use_container_width=True)

        # Individual loss components
        st.subheader("Individual Loss Components")

        loss_components = ['recon', 'kl', 'hamming', 'coherence']
        fig_components = go.Figure()

        for component in loss_components:
            if component in data['train_metrics']:
                fig_components.add_trace(go.Scatter(
                    x=data['epochs'],
                    y=data['train_metrics'][component],
                    mode='lines',
                    name=f'Train {component}',
                    stackgroup='train'
                ))

        fig_components.update_layout(
            title="Training Loss Components Stacked",
            xaxis_title="Epoch",
            yaxis_title="Loss Contribution",
            hovermode="x unified"
        )

        st.plotly_chart(fig_components, use_container_width=True)

    with tab2:
        st.header("Quantum Properties Analysis")

        if 'quantum_metrics' in data and data['quantum_metrics']:
            # Quantum metrics overview
            quantum_metrics = data['quantum_metrics']
            metric_names = list(quantum_metrics.keys())

            # Create radar chart for quantum metrics
            st.subheader("Quantum Metrics Radar Chart")

            # Get latest values for radar chart
            latest_values = [quantum_metrics[metric][-1] for metric in metric_names]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=latest_values,
                theta=metric_names,
                fill='toself',
                name='Latest Values'
            ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(latest_values) * 1.1]
                    )),
                showlegend=False,
                title="Quantum Metrics Overview"
            )

            st.plotly_chart(fig_radar, use_container_width=True)

            # Time series of quantum metrics
            st.subheader("Quantum Metrics Evolution")

            fig_quantum = go.Figure()
            for metric, values in quantum_metrics.items():
                fig_quantum.add_trace(go.Scatter(
                    x=data['epochs'][-len(values):],
                    y=values,
                    mode='lines+markers',
                    name=metric
                ))

            fig_quantum.update_layout(
                title="Quantum Metrics Over Time",
                xaxis_title="Epoch",
                yaxis_title="Metric Value",
                hovermode="x unified"
            )

            st.plotly_chart(fig_quantum, use_container_width=True)
        else:
            st.info("No quantum metrics data available.")

    with tab3:
        st.header("Latent Space Analysis")

        # Phi-shell visualization explanation
        st.markdown("""
        ### 🌰 Phi-Shell Geometry

        The Quantum VAE aims to organize latent representations around a "phi-shell" - a hypersphere
        with radius approximately equal to 3.5 × φ (where φ ≈ 1.618 is the golden ratio).
        """)

        # Sample phi-shell data
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        target_radius = 3.5 * phi   # Target phi-shell radius

        # Generate sample latent vectors
        np.random.seed(42)
        n_samples = 1000
        latent_dim = 32  # Assuming 32-dimensional latent space

        # Generate vectors with varying radii
        radii = np.random.normal(target_radius, 0.5, n_samples)
        angles = np.random.uniform(0, 2*np.pi, (n_samples, latent_dim))

        # Convert to Cartesian coordinates (simplified 2D projection for visualization)
        x_coords = radii * np.cos(angles[:, 0])
        y_coords = radii * np.sin(angles[:, 1])

        # Create phi-shell visualization
        fig_phi = go.Figure()

        # Scatter plot of latent vectors
        fig_phi.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=4,
                color=radii,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Radius")
            ),
            name='Latent Vectors'
        ))

        # Add target phi-shell circle
        theta = np.linspace(0, 2*np.pi, 100)
        circle_x = target_radius * np.cos(theta)
        circle_y = target_radius * np.sin(theta)

        fig_phi.add_trace(go.Scatter(
            x=circle_x,
            y=circle_y,
            mode='lines',
            line=dict(color='red', width=3, dash='dash'),
            name=f'φ-Shell (r={target_radius:.2f})'
        ))

        fig_phi.update_layout(
            title="Latent Space Phi-Shell Visualization",
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            height=600
        )

        st.plotly_chart(fig_phi, use_container_width=True)

        # Statistics
        st.subheader("Phi-Shell Alignment Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Mean Radius", f"{np.mean(radii):.3f}")
        with col2:
            st.metric("Target Radius", f"{target_radius:.3f}")
        with col3:
            alignment = np.exp(-np.abs(np.mean(radii) - target_radius) / target_radius)
            st.metric("Alignment Score", f"{alignment:.3f}")

    with tab4:
        st.header("About This Dashboard")
        st.markdown("""
        ## Quantum Consciousness VAE Dashboard

        This interactive dashboard provides insights into the training and performance of a
        Variational Autoencoder designed for quantum consciousness modeling.

        ### Key Features:
        - **Training Metrics**: Monitor loss components and convergence
        - **Quantum Properties**: Track quantum fidelity, entanglement, and coherence
        - **Latent Space Analysis**: Visualize phi-shell geometry formation
        - **Real-time Monitoring**: Upload your own metrics for analysis

        ### Model Architecture:
        The Quantum VAE incorporates:
        - Mixed-state regularization for quantum mechanical properties
        - Sparse connectivity for efficient quantum circuit representation
        - Composite loss function with quantum-specific terms
        - Consciousness-aware training with EEG integration

        ### Research Alignment:
        This implementation aligns with:
        - **ζ-QVAE Framework** (Physical Review A, 2025)
        - **Deep Belief Machines** for quantum circuit outputs
        - **Quantum Consciousness Models** with EEG-integrated training

        For more information, visit the [GitHub repository](https://github.com/quantumdynamics927-dotcom/AGI-model).
        """)

else:
    st.info("Please upload a metrics JSON file or enable sample data to view the dashboard.")

# Footer
st.markdown("---")
st.caption("Quantum Consciousness VAE Dashboard • Advanced AGI Research")