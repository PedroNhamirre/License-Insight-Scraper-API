from app.schemas.license import LicenseQuery, LicenseResponse
from app.scraper.engine import LicenseScraper


class LicenseService:
    def __init__(self, scraper: LicenseScraper | None = None) -> None:
        self.scraper = scraper or LicenseScraper()

    async def consult(self, query: LicenseQuery) -> LicenseResponse:
        return await self.scraper.fetch_license(query)


def get_license_service() -> LicenseService:
    return LicenseService()
