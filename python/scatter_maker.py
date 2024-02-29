# Script to produce scatter plot of csv data, plotting the same category in clusters
# Satoshi Purkiss Feb 2024

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from scipy.stats import linregress

def calculate_rms(values):
    """Calculate the Root Mean Square of a given set of values."""
    return np.sqrt(np.mean(np.square(values)))

def scatter_plot(x_axis, y_axis_dict, depth_labels, var, variables, output_dir, conv_direction, rms_values_dict, std_values_dict, rms_data, var_unit):
    fig, ax0 = plt.subplots()
    
    var_index = variables.index(var)
    unit = var_unit[var_index]

    # Set labels and tick parameters
    ax0.set_xlabel(f"{var} ({unit})", fontsize=15, labelpad=15)
    ax0.set_ylabel('Temperature (K)', fontsize=15, labelpad=10)
    ax0.tick_params(axis='x', labelsize=12)
    ax0.tick_params(axis='y', labelsize=12)
    ax0.set_ylim(600, 2200)

    # Extract unique values from x_axis and create a mapping to x positions
    unique_x_values = np.unique(x_axis)
    x_pos_mapping = {val: i for i, val in enumerate(unique_x_values)}

    # Base offset for the original data points
    base_offset = 0.04 * (max(x_axis) - min(x_axis))

    for i, depth_label in enumerate(depth_labels):
        # Apply base offset to x-values for the original data points
        x_vals_original = [x + (i * base_offset) for x in x_axis]
        y_vals_original = y_axis_dict[depth_label]

        # Scatter plot for the original data points of each depth range
        ax0.scatter(x_vals_original, y_vals_original, label=f"Original Data {depth_label} km ({conv_direction} Convection)", marker='x', zorder=2, s=20)

        rms_values = rms_values_dict[depth_label]
        std_values = std_values_dict[depth_label]
        # Further offset for RMS values
        rms_offset = (i + 0.5) * base_offset  # Adjust this as needed

        # Apply further offset to x-values for RMS and error bars
        x_vals_rms = [x + rms_offset for x in list(rms_values.keys())]
        y_vals_rms = [rms_values[x] for x in rms_values.keys()]

        # Fit a linear model to the RMS values
        slope, intercept, r_value, p_value, std_err = linregress(x_vals_rms, y_vals_rms)
        line = slope * np.array(x_vals_rms) + intercept

        # Plot the line graph through the RMS values
        ax0.plot(x_vals_rms, line, label=f'Linear Fit {depth_label} km', zorder=3, linewidth=2)
        

        # Plot RMS values and error bars with further offset
        for x_val, rms_val, std_val in zip(x_vals_rms, y_vals_rms, std_values.values()):
            ax0.scatter(x_val, rms_val, color='black', edgecolors='face', linewidths=5, zorder=3+i)
            ax0.errorbar(x_val, rms_val, yerr=std_val/2, elinewidth=2.5, color='black', capsize=5, markersize=10, zorder=4+i)

        # Update RMS, standard deviation, gradient, and R-squared data for DataFrame
        for original_x_val, rms_val in zip(list(rms_values.keys()), y_vals_rms):
            rms_data.append({
                'Depth Label': depth_label,
                'Variable': var,
                'Convection Velocity': conv_direction,
                'X Value': original_x_val,  # Use the original x_val here
                'RMS Value': rms_val,
                'Standard Deviation': std_values[original_x_val],  # Use the original x_val here
                
            })
    
    ax0.spines["top"].set_visible(False)
    ax0.spines["right"].set_visible(False)
    # ax0.set_xticklabels(rms_values[0],fontsize=13)
    # ax0.legend()
    ax0.set_xticks(x_axis.unique())

    plt.tight_layout()
    plt.savefig(output_dir + f'scatter_plot_{var}_{conv_direction}_conv.png', format='png',dpi=300)
    # plt.show()
    plt.close()

def plot_rms_scatter(rms_csv_path, output_dir):
    # Read RMS and Standard Deviation values from CSV
    rms_df = pd.read_csv(rms_csv_path)

    # Get unique attributes
    variables = rms_df['Variable'].unique()
    convection_directions = rms_df['Convection Velocity'].unique()

    # Assign unique colors and markers to each depth range
    depth_styles = {
        '100-200': {'color': 'tab:blue', 'marker': 'o'},
        '200-400': {'color': 'tab:orange', 'marker': 's'}
    }

    # Iterate over each convection direction to create a plot
    for conv_dir in convection_directions:
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Variable positions on the x-axis
        x_positions = np.arange(len(variables))

        for depth_label, style in depth_styles.items():
            # Apply a small offset for each depth range to distinguish them
            depth_offset = -0.05 if depth_label == '100-200' else 0.05

            for i, variable in enumerate(variables):
                # Filter the DataFrame for the current variable, convection direction, and depth label
                subset_df = rms_df[(rms_df['Variable'] == variable) &
                                   (rms_df['Convection Velocity'] == conv_dir) &
                                   (rms_df['Depth Label'] == depth_label)]

                if not subset_df.empty:
                    # Plot each RMS value for the current variable and depth range
                    for index, row in subset_df.iterrows():
                        ax1.errorbar(i + depth_offset, row['RMS Value'], yerr=row['Standard Deviation']/2,
                                    fmt=style['marker'], color=style['color'], capsize=3, label=f'{depth_label} km' if i == 0 and index == 0 else "")

        # Set the x-ticks to correspond to the variables
        ax1.set_xticks(x_positions)
        ax1.set_xticklabels(variables, rotation=30, ha="right",fontsize=13)
        ax1.tick_params(axis='y', labelsize=12)
        ax1.set_ylabel('Average Steady State Temperature RMS (K)',fontsize=13,labelpad=10)
        ax1.set_ylim(1000,2000)
        # ax.set_title(f'RMS Values - {conv_dir} Convection')
        # ax.legend()
        # ax.grid(True)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        plt.tight_layout()
        plt.savefig(output_dir + f'rms_scatter_{conv_dir}_convection.png', format='png',dpi=300)
        # plt.show()
        plt.close()

def main():
    # Load the csv file
    df = pd.read_csv(r"C:\Users\satos\OneDrive - Durham University\Documents\UniStuff\Year 3\Diss\permutations.csv")
    output_dir = r"C:\Users\satos\OneDrive - Durham University\Documents\UniStuff\Year 3\Diss\scatter plots\\"

    # List to store RMS data for DataFrame
    rms_data = []

    # Iterate between depth ranges
    y_axes = ['R values 100-200km', 'R values 200-400km']  # Temperature columns
    depth_labels = ["100-200", "200-400"]

    # For each variable, plot scatter plot, separating Convection Velocity
    variables = ['Lateral Extent', 'Convection Velocity', 'Mantle Interior Starting Temperature', 'Continental Crust Internal Heat Production', 'Continental Crust Thickness']
    variable_units = ['km', 'm/Yr', 'ºC', 'W/m$^3$', 'km']

    for var in variables:
        # Separate data based on Convection Velocity
        df_positive_conv = df[df['Convection Velocity'] > 0]
        df_negative_conv = df[df['Convection Velocity'] < 0]

        y_axis_pos_dict = {depth_label: df_positive_conv[y_axis].values for depth_label, y_axis in zip(depth_labels, y_axes)}
        y_axis_neg_dict = {depth_label: df_negative_conv[y_axis].values for depth_label, y_axis in zip(depth_labels, y_axes)}

        # Initialize dictionaries to store RMS and standard deviation values for each depth range
        rms_values_pos_dict = {}
        std_values_pos_dict = {}
        rms_values_neg_dict = {}
        std_values_neg_dict = {}

        for i, y_axis in enumerate(y_axes):
            # Calculate RMS and standard deviation for each x-axis value (positive convection)
            rms_values_pos = df_positive_conv.groupby(var)[y_axis].apply(calculate_rms).to_dict()
            std_values_pos = df_positive_conv.groupby(var)[y_axis].std().to_dict()
            rms_values_pos_dict[depth_labels[i]] = rms_values_pos
            std_values_pos_dict[depth_labels[i]] = std_values_pos

            # Calculate RMS and standard deviation for each x-axis value (negative convection)
            rms_values_neg = df_negative_conv.groupby(var)[y_axis].apply(calculate_rms).to_dict()
            std_values_neg = df_negative_conv.groupby(var)[y_axis].std().to_dict()
            rms_values_neg_dict[depth_labels[i]] = rms_values_neg
            std_values_neg_dict[depth_labels[i]] = std_values_neg

        # Call the scatter_plot function for positive and negative convection separately
        scatter_plot(df_positive_conv[var], y_axis_pos_dict, depth_labels, var, variables, output_dir, "Positive", rms_values_pos_dict, std_values_pos_dict, rms_data, variable_units)
        scatter_plot(df_negative_conv[var], y_axis_neg_dict, depth_labels, var, variables, output_dir, "Negative", rms_values_neg_dict, std_values_neg_dict, rms_data, variable_units)

    # Create DataFrame and save to CSV
    rms_df = pd.DataFrame(rms_data)
    rms_df.to_csv(output_dir + 'rms_values.csv', index=False)

    plot_rms_scatter(output_dir + 'rms_values.csv', output_dir)

if __name__ == "__main__":
    main()
