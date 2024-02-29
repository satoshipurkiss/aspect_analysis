# Script to automate the process of creating ASPECT input scripts 

# Outputs series of scripts and csv of index number with parameters used 
# Using input csv file with variables and values of variables

# Satoshi Purkiss Jan 2024

import os
import csv
import itertools
import numpy as np
import pandas as pd

# where created ASPECT scripts will be output
output_dir = r'C:\Users\satos\OneDrive - Durham University\Documents\UniStuff\Year 3\Diss\Code\automated\\'

# input file is vector of 5 variables, 3 values each: 
# 1 Box size, 2 Convection Speed, 3 Start Temp, 4 Continent Internal Heating, 5 Continent Thickness
input_file = r"C:\Users\satos\OneDrive - Durham University\Documents\UniStuff\Year 3\Diss\Code\input_file.csv"

def process(parameters, index):
    output_file = "v5_{:03d}__{}__{}__{}__{}__{}".format(index,*parameters)
    output_file = output_file.replace('-','L')  # ASPECT doesn't like - and . in its directory naming 
    output_file = output_file.replace('.', '_')

    x_extent = parameters[0]    # x extent
    oceanic_x_extent = 2*x_extent/3

    convection_speed = parameters[1] # convection speed 

    start_heat = parameters[2] # start internal heating 
    h=3000000               # height of model
    Ttop = 273              # temp at surface
    Tmid = start_heat+273   # intermediate start temp
    Tbot = 2723             # temp at core/mantle boundary
    z0 = 0                  # distance to core/mantle boundary
    z1 = h * 0.1            # distance to 10% above core/mantle boundary
    z2 = h * 0.9            # distance to 10& below surface
    z3 = h                  # distance to surface
    heat_A = (Tbot - Tmid)/(z0-z1)   # top gradient
    heat_B = (Tbot -Ttop)            
    heat_C = (Tmid - Ttop)/(z2-z3)   # bottom gradient
    heat_D = (Ttop-heat_C*z3 - Ttop) 

    cont_int_heat = (parameters[3])*0.0000001 # internal heating of the continental crust (W/m^3)
    cont_dens = 3350        # density of continental crust (kg/m^3)
    cont_thickness = parameters[4]  # thickness of continental crust (m)

    # default ASPECT script with wildcards where variables are changeable 
    default = f"""
    # Input file for ASPECT
    # Jeroen van Hunen October 2023
    # Modified by Satoshi Purkiss January 2024

    # This runs convection dimensionally in a box of 15000km depth
    # with a moving top left boundary
    # Bottom temp is 2450C

    # Parameters varied are:
    # Box x extent                      (m)
    # Convection speed and direction    (m/year)
    # Mantle starting temperature       (C)
    # Continental crust internal radiogenic heating (W/m^3)
    # Continental crust density         (kg/m^3)
    # Continental crust thickness       (m)

    # Set Global parameters
    set Dimension                              = 2
    set Start time                             = 0
    set End time                               = 1000000000
    set Use years in output instead of seconds = true
    set Nonlinear solver scheme                = iterated Stokes
    set Nonlinear solver tolerance             = 1e-4
    set Max nonlinear iterations               = 1
    set CFL number                             = 0.5
    set Output directory                       = {output_file}
    set Timing output frequency                = 20
    set Pressure normalization                 = no

    # Stokes solver parameters:
    subsection Solver parameters
    subsection Stokes solver parameters
        set Linear solver tolerance = 1e-7
        set Number of cheap Stokes solver steps = 0
    end
    end

    # Set up the model domain
    subsection Geometry model
    set Model name = box
    subsection Box
        set X repetitions = 5
        set Y repetitions = 1
        set X extent      = {x_extent}
        set Y extent      = 3000000
        set X periodic    = false
    end
    end
    # Create a finite element mesh
    subsection Mesh refinement
    set Initial adaptive refinement        = 0
    set Initial global refinement          = 6
    set Time steps between mesh refinement = 0
    end

    # Create composition for continental lithosphere
    subsection Compositional fields
    set Number of fields	= 1
    set Names of fields	= continent
    end

    subsection Initial composition model
    set Model name = function
    subsection Function
        set Function constants = h = 3000000, w = {x_extent}

        set Variable names      = 	x,y
        set Function expression = if( x>(2*w/3) && y>(h-{cont_thickness}), 1, 0)
    end
    end



    # Set boundary conditions for the heat equation
    subsection Boundary temperature model
    set List of model names = box
    subsection Box
        set Bottom temperature = 2723
        set Top temperature    = 273
    end
    set Fixed temperature boundary indicators   = bottom, top
    end

    # Set boundary conditions for the Stokes equation
    subsection Boundary velocity model
    set Tangential velocity boundary indicators = left, right, bottom
    set Prescribed velocity boundary indicators = top: function
    
    subsection Function
        set Variable names      = x,z,t
        set Function expression = if(x<{oceanic_x_extent}, {convection_speed},0); 0
    end
    end


    # Set the initial temperature field
    subsection Initial temperature model
    set Model name = function

    subsection Function
        set Variable names      = x,z
        set Function constants  = p=0.01, L=15000000, pi=3.1415926536, k=1, T0=273, h=3000000, A={heat_A}, B={heat_B}, C={heat_C}, D={heat_D}
        set Function expression = if(z<0.1*h, T0 + A*z+B - p*cos(k*pi*x/L)*sin(pi*z/h),\\
                                if(z>0.9*h, T0 + C*z+D - p*cos(k*pi*x/L)*sin(pi*z/h),\\
                                T0 + {start_heat} - p*cos(k*pi*x/L)*sin(pi*z/h)))
    end
    end

    # Constant internal heat production values (W/m^3)
    subsection Heating model
    set List of model names = compositional heating
    subsection Compositional heating
        set Compositional heating values = 6e-9, {cont_int_heat}
    end
    end

    # Define the material in the box:
    subsection Material model
    set Model name = visco plastic

    subsection Visco Plastic
        set Viscous flow law = diffusion

        set Reference temperature = 293
        set Reference strain rate = 1.e-16

        set Minimum viscosity = 1e18
        set Maximum viscosity = 1e24

        set Thermal diffusivities = 1e-6
        set Heat capacities       = 1000.
        set Densities             = 3400, {cont_dens}
        set Thermal expansivities = 3e-5

        set Viscosity averaging scheme = harmonic

        set Prefactors for diffusion creep           = 5e-23, 5e-25
        set Activation energies for diffusion creep  = 0.
        set Activation volumes for diffusion creep   = 0.
        set Grain size                               = 1.
        set Grain size exponents for diffusion creep = 0.

        set Angles of internal friction = 0
        set Cohesions                   = 1e20
        set Maximum yield stress        = 1e20
    end
    end

    # Set the gravity field
    subsection Gravity model
    set Model name = vertical
    subsection Vertical
        set Magnitude = 9.81
    end
    end

    # Some more model formulations
    subsection Formulation
    set Formulation = Boussinesq approximation
    end

    # Tell ASPECT which results to output, and in which format
    subsection Postprocess
    set List of postprocessors = velocity statistics, basic statistics, temperature statistics, visualization, heat flux statistics, depth average
    subsection Visualization
        set List of output variables = density, viscosity, strain rate, error indicator, melt fraction
        set Output format = vtu
        set Time between graphical output = 20000000
        set Interpolate output = true
        set Number of grouped files       = 1
    subsection Melt fraction
        set A1 = 1085.7
        set A2 = 1.174e-7
        end
    end
    end
    """

    # Writing the file to specifiec directory
    file_path = output_dir+"v5_curtain_{:03d}_{}_{}_{}_{}_{}.prm".format(index,*parameters)
    with open(file_path, 'w') as file:
        file.write(default)

    # print(f"String saved to {file_path}")

# To rename the files for indexing
def rename_files_in_folder(folder_path):
    # List all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Iterate over the files and rename them
    for index, filename in enumerate(files, start=1):
        # Create the new filename with a number prefix
        new_filename = f"parameters{index:03d}.prm"
        
        # Full path for the old and new filenames
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_file, new_file)
        # print(f"Renamed '{filename}' to '{new_filename}'")

# Write index and parameters used to csv
def write_to_csv(filename, data):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['Index'] + [f'Variable_{i+1}' for i in range(len(data[0]) - 1)]
        writer.writerow(header)

        for row in data:
            writer.writerow(row)

def main():
    df = np.array(pd.read_csv(input_file))

    csv_data = []
    index = 1

    for perm in list(itertools.product(*df)):
        process(perm, index)
        csv_data.append([index] + list(perm))
        index += 1 # Increment index

    # for negative (left/anticlockwise) convection:
        neg_perm = list(perm)
        neg_perm[1] = -neg_perm[1]
        process(neg_perm, index)
        csv_data.append([index] + list(neg_perm))
        index += 1 # Increment index

    write_to_csv(output_dir+r"..\\"+'permutations.csv', csv_data)
    rename_files_in_folder(output_dir)


if __name__ == "__main__":
    main()