# just plotting the inital temp 
# satoshi purkiss feb 2024

import numpy as np
import matplotlib.pyplot as plt

def main():
    # Constants
    p = 0.01
    L = 15000000
    pi = np.pi
    k = 1
    T0 = 0
    h = 3000000
    A = -0.0036666666666666666
    B = 2450
    C = -0.0045
    D = 13499.999999999998
    x = 0  # Assuming x is constant for this plot

    output_dir = r"C:\Users\satos\OneDrive - Durham University\Documents\UniStuff\Year 3\Diss\\"

    # Function definition
    def temperature(z):
        
        if z < 0.1 * h:
            return T0 + A * z + B - p * np.cos(k * pi * x / L) * np.sin(pi * z / h)
        elif z > 0.9 * h:
            return T0 + C * z + D - p * np.cos(k * pi * x / L) * np.sin(pi * z / h)
        else:
            return T0 + 1350.0 - p * np.cos(k * pi * x / L) * np.sin(pi * z / h)

    # Generate a range of z values
    z_values = np.array(np.linspace(0, h, 500))
    # z_values = np.flip(z_values)

    # Calculate temperature for each z
    temperatures = np.flip([temperature(z) for z in z_values])
    

    # Plotting
    fig, axs = plt.subplots()
    # axs.figure(figsize=(8, 6))
    axs.plot(temperatures, z_values/1000,color='red')
    axs.set_xlabel('Temperature (ºC)')
    axs.set_ylabel('Depth (km)')
    # axs.title('Initial Temperature Variation with Depth')
    # axs.grid(True)

    axs.spines["top"].set_visible(False)
    axs.spines["right"].set_visible(False)

    plt.gca().invert_yaxis()  # Invert y-axis to have depth increase downwards
    plt.tight_layout()
    # plt.show()    
    plt.savefig(output_dir + 'initial temp variation with depth.png', format='png',dpi=300)


if __name__ == "__main__":
    main()