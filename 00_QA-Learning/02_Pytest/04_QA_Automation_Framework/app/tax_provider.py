class TaxRateProvider:

    def get_tax_rate(self, country_code):
        raise NotImplementedError


class StaticTaxRateProvider(TaxRateProvider):
    RATES = {"PL": 23, "DE": 19, "FR": 20, "GB": 20, "US": 0}

    def get_tax_rate(self, country_code):
        return self.RATES.get(country_code)
