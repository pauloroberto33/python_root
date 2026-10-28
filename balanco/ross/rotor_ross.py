import ross as rs
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
from ross.units import Q_

pio.renderers.default = "browser"

steel = rs.Material(name="Steel", rho=7860, E=192e9, G_s=81.2e9)

L = [25, 5, 29.5, 5.5, 16.6, 48, 19.9, 52.5, 6, 12, 10, 34, 14, 67, 20, 100, 45, 40, 85, 80, 15, 15, 52.7,
     19.8, 13.6, 19.8, 13.6, 19.8, 13.6, 19.8, 17.2, 21.7, 19.6, 9.2, 71.4, 20.5, 14.5, 20.5, 18.3, 26, 18.3,
     26.2, 45.6, 21.5, 36.7, 81, 61, 20, 65, 14, 39, 45, 20, 45, 45, 15, 15, 15, 1.5]
idl = [0] * len(L)
odl = [150, 65, 65, 65, 54, 54, 122, 54, 90, 90, 90, 90, 157, 120, 160, 160, 250, 250, 250, 250, 340, 340, 200,
       188.6, 156.7, 188.6, 157, 188.6, 156.7, 188.6, 156.7, 200, 200, 218.4, 218.4, 209.6, 176.7, 208.6, 167.6,
       208.6, 167.6, 220, 220, 229.9, 250, 160, 160, 160, 120, 157, 90, 90, 170, 90, 90, 120, 150, 199, 161]
N = len(L)

shaft_elements = [    rs.ShaftElement(
        L=L[i]/1000,
        idl=idl[i]/1000,
        odl=odl[i]/1000,
        material=steel,
        shear_effects=True,
        rotary_inertia=True,
        gyroscopic=True,
    )
    for i in range(N)
]

dados_discos_corrigidos = [
    (21, 1.3, 0.0205, 0.041),
    (25, 2.5, 0.0155, 0.031),
    (27, 2.8, 0.0180, 0.036),
    (29, 3.0, 0.0205, 0.041),
    (31, 3.0, 0.0205, 0.041),
    (37, 3.2, 0.0240, 0.048),
    (39, 4.5, 0.0345, 0.069),
    (41, 4.8, 0.0385, 0.077)
]

disks = [
    rs.DiskElement(n=estacao, m=massa, Id=Id, Ip=Ip)
    for estacao, massa, Id, Ip in dados_discos_corrigidos
]

bearing_speed = 12000 * 2 * np.pi / 60

bearing0 = rs.BearingElement(
    n=11,
    kxx=[2.92e8],
    kyy=[2.92e8],
    cxx=[1.70e5],
    cyy=[1.7e5],
    speed=[bearing_speed],
)
bearing1 = rs.BearingElement(
    n=51,
    kxx=[2.92e8],
    kyy=[2.92e8],
    cxx=[1.70e5],
    cyy=[1.7e5],
    speed=[bearing_speed],
)
bearings = [bearing0, bearing1]

rotor = rs.Rotor(
    shaft_elements=shaft_elements, disk_elements=disks, bearing_elements=bearings
)

max_speed_rad_s = 20000 * 2 * np.pi / 60
speed_range = np.linspace(100, max_speed_rad_s, 100)

campbell = rotor.run_campbell(speed_range=speed_range)
static_results = rotor.run_static()

critical_speed = rotor.run_critical_speed(num_modes=2)
print("Velocidades críticas não amortecidas (RPM):", critical_speed.wn("RPM"))
print("Velocidades críticas amortecidas (RPM):", critical_speed.wd("RPM"))

no_apl = 30
magnitude = 0.0007
fase = 0.0

observation_node = 51

resposta = rotor.run_unbalance_response(
    node=no_apl,
    unbalance_magnitude=magnitude,
    unbalance_phase=fase,
    speed_range=speed_range
)

fig_rotor = rotor.plot_rotor()
fig_rotor.show()

fig_campbell = campbell.plot()
fig_campbell.show()

# Gerar e exibir a deformada estática do rotor
fig_static = static_results.plot_deformation()
fig_static.show()

#################################################################################
# ==================================================
# 1. ANÁLISE ESTÁTICA

# Imprimir forças de reação nos mancais
print("\n" + "=" * 65)
print("REAÇÕES ESTÁTICAS DOS MANCAIS")
print("=" * 65)

print("\nForças por nó:")
print(static_results.bearing_forces)

print("\nForças por mancal:")
print(static_results.bearing_forces)

# ==================================================
# 2. FLECHA ESTÁTICA DO ROTOR
# ==================================================
# Deslocamento vertical devido à gravidade
flecha = np.asarray(static_results.deformation).ravel()

# Coordenadas axiais dos nós do rotor
posicoes = np.array([
    elemento.n_l
    for elemento in rotor.shaft_elements
])

# Imprimir deslocamentos em micrômetros
print("\n" + "=" * 65)
print("FLECHA ESTÁTICA DO ROTOR")
print("=" * 65)

for i, deslocamento in enumerate(flecha):
    print(
        f"Índice DOF/nó {i:3d}: "
        f"{deslocamento * 1e6:12.4f} µm"
    )

print(
    f"\nFlecha máxima absoluta: "
    f"{np.max(np.abs(flecha)) * 1e6:.4f} µm"
)
#################################################################################

# Orientação 0 rad: direção X
#probe_x = rs.Probe(no_apl, Q_(np.pi/4, "rad"))
probe_x = rs.Probe(no_apl, Q_(0, "rad"), tag="X")
# Orientação pi/2 rad: direção Y
#probe_y = rs.Probe(no_apl, Q_(3*np.pi / 4, "rad"))
probe_y = rs.Probe(no_apl, Q_(np.pi / 2, "rad"), tag="Y")

# --------------------------------------------------
# 6. Plotar diagramas de Bode
# --------------------------------------------------
fig = resposta.plot(probe=[probe_x, probe_y])
fig.show()

# Amplitude versus rotação
fig_amp = resposta.plot_magnitude(probe=[probe_x, probe_y])
fig_amp.show()

# Fase versus rotação
fig_phase = resposta.plot_phase(probe=[probe_x, probe_y])
fig_phase.show()

# --------------------------------------------------
# 7. Forma deformada do rotor em uma rotação
# --------------------------------------------------
# Converter a rotação alvo desejada de RPM para rad/s
target_rpm = 12000.0
target_speed_rad_s = target_rpm * 2.0 * np.pi / 60.0

# Identificar dinamicamente a rotação calculada mais próxima no speed_range original
idx_speed = np.argmin(np.abs(speed_range - target_speed_rad_s))
selected_speed_rad_s = speed_range[idx_speed]

# Apresentar a forma deformada 3D do rotor na velocidade aproximada resolvida
fig_3d = resposta.plot_deflected_shape_3d(speed=selected_speed_rad_s)
fig_3d.show()



# Selecionando uma rotação representativa (ex: aproximadamente 10.000 RPM)
target_rpm = 12000.0
rpm_axis = speed_range * 60.0 / (2.0 * np.pi)
idx = np.argmin(np.abs(rpm_axis - target_rpm))
selected_rpm = rpm_axis[idx]
selected_omega = speed_range[idx]


# Nó 11 (Mancal 1)
node = 51
dof_x = 6 * node
dof_y = 6 * node + 1

'''
number_dof = rotor.number_dof
dof_x = number_dof * observation_node
dof_y = dof_x + 1
'''
# Resposta complexa (m) no índice selecionado
z_x = resposta.forced_resp[dof_x, idx]
z_y = resposta.forced_resp[dof_y, idx]

# Reconstrução temporal sobre um período orbital (T = 2*pi/omega)
t_plot = np.linspace(0, 2 * np.pi / selected_omega, 200)

# Resposta harmônica real no tempo: x(t) = Re( z_x * exp(i * omega * t) )
x_t = np.real(z_x * np.exp(1j * selected_omega * t_plot)) * 1e6  # para micrometros
y_t = np.real(z_y * np.exp(1j * selected_omega * t_plot)) * 1e6  # para micrometros

# Plotagem da Órbita
plt.figure(figsize=(7, 7))
plt.plot(x_t, y_t, label=f'Órbita @ {selected_rpm:.0f} RPM', color='blue', linewidth=2)
plt.scatter([0], [0], color='red', marker='+', s=150, label='Centro Geométrico')
plt.scatter([x_t[0]], [y_t[0]], color='green', marker='o', s=80, label='Posição Inicial (t=0)')

plt.xlabel('Deslocamento X [µm]')
plt.ylabel('Deslocamento Y [µm]')
plt.title(f'Órbita do Rotor no Nó: {node}\nVelocidade: {selected_rpm:.0f} RPM')
plt.grid(True, linestyle='--', alpha=0.5)
plt.axis('equal')
plt.legend()
plt.show()