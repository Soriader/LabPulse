import pandas as pd

UNIT_RULES = {
    'Water': 'mg/kg',
    'Sulfur': 'mg/kg',
    'Chloride': 'mg/kg',
    'Ash': '% m/m',
    'Viscosity': 'cSt'
}

def apply_unit_rules(df: pd.DataFrame, rules: dict = UNIT_RULES) -> pd.DataFrame:
    """
    Apply QC unit validation rules.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'parameter' and 'unit' columns.
    rules : dict
        Mapping of parameter -> expected unit.

    Returns
    -------
    pd.DataFrame
        Copy of DataFrame with added columns:
        - expected_unit
        - unit_ok
    """

    df_copy = df.copy()

    df_copy["expected_unit"] = df_copy["parameter"].map(rules)

    # unit_ok is True only if:
    # - a rule exists for the parameter
    # - reported unit matches the expected unit
    df_copy["unit_ok"] = (
        df_copy["expected_unit"].notna()
        & (df_copy["unit"] == df_copy["expected_unit"])
    )

    return df_copy
