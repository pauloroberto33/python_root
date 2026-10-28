"""Cálculos de eficiência e transferência de calor para o editor de balanço."""


def turbine_efficiency(h_in: float, h_out: float, h_is: float) -> float:
    """Retorna a eficiência isentrópica da turbina em porcentagem."""
    ideal_drop = h_in - h_is
    if ideal_drop == 0:
        raise ValueError("A queda de entalpia isentrópica não pode ser zero.")
    return (h_in - h_out) / ideal_drop * 100


def pump_efficiency(h_in: float, h_out: float, h_is: float) -> float:
    """Retorna a eficiência isentrópica da bomba em porcentagem."""
    actual_rise = h_out - h_in
    if actual_rise == 0:
        raise ValueError("O aumento real de entalpia da bomba não pode ser zero.")
    return (h_is - h_in) / actual_rise * 100


def preheater_effectiveness(h_in: float, h_out: float, h_target: float) -> float:
    """Retorna a efetividade do preaquecedor em porcentagem."""
    maximum_rise = h_target - h_in
    if maximum_rise == 0:
        raise ValueError("A entalpia-alvo deve ser diferente da entalpia de entrada.")
    return (h_out - h_in) / maximum_rise * 100


def heat_duty(mass_flow: float, h_in: float, h_out: float) -> float:
    """Calcula a taxa de calor em MW para vazão em kg/s e entalpia em kJ/kg."""
    return mass_flow * (h_out - h_in) / 1000
