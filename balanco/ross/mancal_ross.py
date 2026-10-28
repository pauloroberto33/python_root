import ross as rs
from ross.units import Q_

# Create a five-pad radial tilting-pad bearing
print("Calculando o mancal... esta etapa pode levar alguns minutos.", flush=True)
bearing = rs.TiltingPad(
    n=11,
    speed=Q_([3000], "RPM"),
    equilibrium_type="match_load",
    thermal_type="full",
    journal_diameter=101.6e-3,
    radial_clearance=74.9e-6,
    pad_thickness=12.7e-3,
    pivot_angle=Q_([18, 90, 162, 234, 306], "deg"),
    pad_arc=Q_([60, 60, 60, 60, 60], "deg"),
    pad_axial_length=[50.8e-3] * 5,
    preload=[0.5] * 5,
    offset=[0.5] * 5,
    lubricant="ISOVG32",
    oil_supply_temperature=Q_(40, "degC"),
    oil_flow_v=Q_(10, "l/min"),
    fxs_load=884.05,
    fys_load=-2670.4,
    total_ex_film=20,
    total_ez_film=10,
    total_ey_pad=10,
    total_ey_film=10,
    journal_temperature=Q_(25, "degC"),
    pad_conductivity=45.0,
    edges_convection=2000.0,
)

# Summary of the bearing solution
bearing.show_results()

# Dynamic coefficients at each analyzed speed
bearing.show_coefficients_comparison()

# Numerical execution time
bearing.show_execution_time()

# Pressure and temperature fields
bearing.plot_pressure_2d()
bearing.plot_temperature_2d()

# 3D oil-film pressure distribution
fig_pressure = bearing.plot_pressure_3d()
fig_pressure.show()

# 3D oil-film temperature distribution
fig_temperature = bearing.plot_film_temperature_3d()
fig_temperature.show()

# 3D pad temperature distribution, if supported by the thermal model
fig_pads = bearing.plot_pad_temperature_3d()
fig_pads.show()