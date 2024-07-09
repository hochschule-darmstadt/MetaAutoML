import streamlit as st
import os
import sys
import streamlit.components.v1 as components

st.title('Cluster Evaluation Dashboard')

plot_types = ['cluster', 'tsne', 'elbow', 'silhouette', 'distance', 'distribution']

# Read the path from the arguments.
if len(sys.argv) > 1:
    save_directory = sys.argv[1]
else:
    st.error("Save directory not provided")
    save_directory = None

if save_directory is not None:
    for plot_type in plot_types:
        st.header(f"{plot_type.capitalize()} Plot")
        if plot_type in ['elbow', 'silhouette', 'distance']:
            image_path = os.path.join(save_directory, f'{plot_type}.png')
            if os.path.exists(image_path):
                st.image(image_path, caption=f"{plot_type.capitalize()} Plot")
            else:
                st.error(f"Image file for {plot_type} does not exist.")
        else:
            html_path = os.path.join(save_directory, f'{plot_type}.html')
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    components.html(html_content, height=600)
            else:
                st.error(f"HTML file for {plot_type} does not exist.")

        # Add description
        if plot_type == 'cluster':
            description = "This PCA plot provides a 2-dimensional projection of the dataset where clusters of data points are formed based on their principal components. It's useful for visualizing the overall structure and separation of clusters in lower dimensions, which aids in identifying inherent groupings within the data."
        elif plot_type == 'tsne':
            description = "This plot uses t-SNE for a 3-dimensional visualization of high-dimensional data, effectively capturing complex structures in a form that's easier to interpret. It helps in understanding the grouping and separation of data points in multiple dimensions, offering insights into data density and distribution."
        elif plot_type == 'elbow':
            description = "The Elbow plot shows the sum of squared distances of samples to their closest cluster center, which decreases as the number of clusters increases. This plot is crucial for determining the optimal number of clusters by identifying the 'elbow' point where adding more clusters does not significantly improve the fit."
        elif plot_type == 'silhouette':
            description = "Silhouette analysis measures the similarity of an object to its own cluster compared to other clusters. A high silhouette value indicates that the object is well matched to its own cluster and poorly matched to neighboring clusters. This plot is essential for evaluating the adequacy of the clustering and the separation between the clusters."
        elif plot_type == 'distance':
            description = "This visualization displays the distances between points within each cluster. It's used to assess the compactness and separation of the clusters, highlighting how tightly grouped the elements of each cluster are, which can indicate the quality of the clustering process."
        elif plot_type == 'distribution':
            description = "Distribution plots provide visual insights into the statistical distribution, skewness, and kurtosis of the data points across different variables or clusters. These plots are key for analyzing the spread of data, identifying outliers, and understanding the central tendency, which can influence clustering decisions."

        st.write(description)
