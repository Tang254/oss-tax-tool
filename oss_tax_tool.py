import argparse
from pathlib import Path

import pandas as pd


JTL_COLUMN_VARIATIONS = {
    "currency": ["AuftragswÃ¤hrung", "Auftragswahrung", "AuftragsWaehrung", "Auftragswährung"],
    "country": ["LA Land ISO"],
    "shipping_country": ["Versandland LÃ¤nder ISO", "Versandland Lander ISO", "Versandland Länder ISO"],
    "vat_free": ["USt.frei"],
    "net_amount": ["Gesamtbetrag Netto (alle Ust.)"],
    "vat_amount": ["Betrag USt. (2 Nachkommastellen)"],
}

DOMESTIC_VAT_COUNTRIES = {
    "FR": 0.20,
    "IT": 0.22,
    "PL": None,
    "CZ": None,
    "ES": 0.21,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate OSS or domestic EU VAT totals from JTL invoice exports and Amazon tax reports."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["oss", "domestic"],
        help="oss: cross-border OSS totals, domestic: selected domestic VAT totals.",
    )
    parser.add_argument("--jtl-file", required=True, help="Path to the JTL invoice CSV export.")
    parser.add_argument("--amazon-file", required=True, help="Path to the Amazon VAT transaction CSV export.")
    parser.add_argument(
        "--output",
        help="Optional output CSV path. Defaults to a timestamped file in the current directory.",
    )
    parser.add_argument(
        "--countries",
        nargs="*",
        default=list(DOMESTIC_VAT_COUNTRIES.keys()),
        help="Countries used in domestic mode. Default: FR IT PL CZ ES",
    )
    return parser.parse_args()


def find_columns(df: pd.DataFrame, variations: dict[str, list[str]]) -> dict[str, str]:
    column_mapping: dict[str, str] = {}
    for key, candidates in variations.items():
        for candidate in candidates:
            if candidate in df.columns:
                column_mapping[key] = candidate
                break
        if key not in column_mapping:
            available = ", ".join(df.columns.astype(str).tolist())
            raise ValueError(f"Missing required column for '{key}'. Available columns: {available}")
    return column_mapping


def convert_jtl_sum(series: pd.Series) -> float:
    if series.dtype == "object":
        values = series.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        sum_value = pd.to_numeric(values, errors="coerce").sum()
    else:
        sum_value = pd.to_numeric(series, errors="coerce").sum()
    return float(sum_value) / 100.0


def load_jtl_data(file_path: str) -> tuple[pd.DataFrame, dict[str, str]]:
    df = pd.read_csv(
        file_path,
        encoding="ISO-8859-1",
        sep=";",
        decimal=",",
        thousands=".",
        low_memory=False,
    )
    return df, find_columns(df, JTL_COLUMN_VARIATIONS)


def load_amazon_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(
        file_path,
        encoding="ISO-8859-1",
        sep=",",
        header=0,
        decimal=".",
        low_memory=False,
    )


def calculate_oss_from_jtl(df: pd.DataFrame, columns: dict[str, str]) -> list[tuple[str, str, float, float]]:
    results: list[tuple[str, str, float, float]] = []
    countries = df[columns["country"]].dropna().unique()

    for country in countries:
        country_df = df[
            (df[columns["shipping_country"]] != country)
            & (df[columns["country"]] == country)
            & (df[columns["vat_free"]] == 0)
            & (df[columns["vat_amount"]] != 0)
        ]

        for currency in country_df[columns["currency"]].dropna().unique():
            filtered_df = country_df[country_df[columns["currency"]] == currency]
            net_total = convert_jtl_sum(filtered_df[columns["net_amount"]])
            vat_total = convert_jtl_sum(filtered_df[columns["vat_amount"]])
            if net_total != 0 or vat_total != 0:
                results.append((str(country), str(currency), net_total, vat_total))

    return results


def calculate_domestic_from_jtl(
    df: pd.DataFrame,
    columns: dict[str, str],
    countries: list[str],
) -> list[tuple[str, str, float, float]]:
    results: list[tuple[str, str, float, float]] = []

    for country in countries:
        country_df = df[
            (df[columns["shipping_country"]] == country)
            & (df[columns["country"]] == country)
            & (df[columns["vat_free"]] == 0)
            & (df[columns["vat_amount"]] != 0)
        ]

        for currency in country_df[columns["currency"]].dropna().unique():
            filtered_df = country_df[country_df[columns["currency"]] == currency]
            net_total = convert_jtl_sum(filtered_df[columns["net_amount"]])
            vat_total = convert_jtl_sum(filtered_df[columns["vat_amount"]])
            if net_total != 0 or vat_total != 0:
                results.append((country, str(currency), net_total, vat_total))

    return results


def calculate_oss_refunds(df: pd.DataFrame) -> list[tuple[str, str, float, float]]:
    refund_df = df[df["TRANSACTION_TYPE"] == "REFUND"]
    results: list[tuple[str, str, float, float]] = []

    for country in refund_df["SALE_ARRIVAL_COUNTRY"].dropna().unique():
        filtered_df = refund_df[
            (refund_df["SALE_DEPART_COUNTRY"] != country)
            & (refund_df["SALE_ARRIVAL_COUNTRY"] == country)
            & (refund_df["TOTAL_ACTIVITY_VALUE_VAT_AMT"] != 0)
        ]
        net_total = float(filtered_df["TOTAL_ACTIVITY_VALUE_AMT_VAT_EXCL"].sum())
        vat_total = float(filtered_df["TOTAL_ACTIVITY_VALUE_VAT_AMT"].sum())
        if net_total != 0 or vat_total != 0:
            results.append((str(country), "EUR", net_total, vat_total))

    return results


def calculate_domestic_refunds(df: pd.DataFrame, countries: list[str]) -> list[tuple[str, str, float, float]]:
    refund_df = df[df["TRANSACTION_TYPE"] == "REFUND"]
    results: list[tuple[str, str, float, float]] = []

    for country in countries:
        vat_rate = DOMESTIC_VAT_COUNTRIES.get(country)
        filtered_df = refund_df[
            (refund_df["SALE_DEPART_COUNTRY"] == country)
            & (refund_df["SALE_ARRIVAL_COUNTRY"] == country)
        ]
        if vat_rate is not None:
            filtered_df = filtered_df[filtered_df["PRICE_OF_ITEMS_VAT_RATE_PERCENT"] == vat_rate]

        net_total = float(filtered_df["TOTAL_ACTIVITY_VALUE_AMT_VAT_EXCL"].sum())
        vat_total = float(filtered_df["TOTAL_ACTIVITY_VALUE_VAT_AMT"].sum())
        if net_total != 0 or vat_total != 0:
            results.append((country, "EUR", net_total, vat_total))

    return results


def combine_results(
    invoice_results: list[tuple[str, str, float, float]],
    refund_results: list[tuple[str, str, float, float]],
) -> pd.DataFrame:
    combined: dict[tuple[str, str], dict[str, float]] = {}

    for country, currency, net_total, vat_total in invoice_results:
        key = (country, currency)
        combined.setdefault(
            key,
            {
                "invoice_net": 0.0,
                "invoice_vat": 0.0,
                "refund_net": 0.0,
                "refund_vat": 0.0,
                "total_net": 0.0,
                "total_vat": 0.0,
            },
        )
        combined[key]["invoice_net"] += net_total
        combined[key]["invoice_vat"] += vat_total
        combined[key]["total_net"] += net_total
        combined[key]["total_vat"] += vat_total

    for country, currency, net_total, vat_total in refund_results:
        key = (country, currency)
        combined.setdefault(
            key,
            {
                "invoice_net": 0.0,
                "invoice_vat": 0.0,
                "refund_net": 0.0,
                "refund_vat": 0.0,
                "total_net": 0.0,
                "total_vat": 0.0,
            },
        )
        combined[key]["refund_net"] += net_total
        combined[key]["refund_vat"] += vat_total
        combined[key]["total_net"] += net_total
        combined[key]["total_vat"] += vat_total

    rows = []
    for (country, currency), values in sorted(combined.items()):
        rows.append(
            {
                "Country": country,
                "Currency": currency,
                "Invoice_Net": values["invoice_net"],
                "Invoice_VAT": values["invoice_vat"],
                "Refund_Net": values["refund_net"],
                "Refund_VAT": values["refund_vat"],
                "Total_Net": values["total_net"],
                "Total_VAT": values["total_vat"],
            }
        )

    return pd.DataFrame(rows)


def default_output_path(mode: str) -> Path:
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    return Path(f"{mode}_results_{timestamp}.csv")


def run_calculation(
    mode: str,
    jtl_file: str,
    amazon_file: str,
    output: str | None = None,
    countries: list[str] | None = None,
) -> tuple[pd.DataFrame, Path]:
    selected_countries = [country.upper() for country in (countries or list(DOMESTIC_VAT_COUNTRIES.keys()))]
    jtl_df, jtl_columns = load_jtl_data(jtl_file)
    amazon_df = load_amazon_data(amazon_file)

    if mode == "oss":
        invoice_results = calculate_oss_from_jtl(jtl_df, jtl_columns)
        refund_results = calculate_oss_refunds(amazon_df)
    elif mode == "domestic":
        invoice_results = calculate_domestic_from_jtl(jtl_df, jtl_columns, selected_countries)
        refund_results = calculate_domestic_refunds(amazon_df, selected_countries)
    else:
        raise ValueError("mode must be 'oss' or 'domestic'")

    result_df = combine_results(invoice_results, refund_results)
    if result_df.empty:
        raise ValueError("No matching records found.")

    output_path = Path(output) if output else default_output_path(mode)
    result_df.to_csv(output_path, index=False, decimal=",", float_format="%.2f")
    return result_df, output_path


def main() -> None:
    args = parse_args()
    result_df, output_path = run_calculation(
        mode=args.mode,
        jtl_file=args.jtl_file,
        amazon_file=args.amazon_file,
        output=args.output,
        countries=args.countries,
    )

    print(result_df.to_string(index=False))
    print(f"\nSaved results to: {output_path}")


if __name__ == "__main__":
    main()
