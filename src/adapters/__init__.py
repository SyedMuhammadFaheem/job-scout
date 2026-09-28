from src.adapters.arbeitnow import ArbeitnowAdapter
from src.adapters.google_alerts import GoogleAlertsAdapter
from src.adapters.greenhouse import GreenhouseAdapter
from src.adapters.himalayas import HimalayasAdapter
from src.adapters.hn_hiring import HNHiringAdapter
from src.adapters.jobicy import JobicyAdapter
from src.adapters.lever import LeverAdapter
from src.adapters.remoteok import RemoteOKAdapter
from src.adapters.remotive import RemotiveAdapter
from src.adapters.weworkremotely import WeWorkRemotelyAdapter

# Maps config.json "sources" keys -> adapter class
ADAPTER_REGISTRY = {
    "remoteok": RemoteOKAdapter,
    "remotive": RemotiveAdapter,
    "arbeitnow": ArbeitnowAdapter,
    "jobicy": JobicyAdapter,
    "weworkremotely": WeWorkRemotelyAdapter,
    "himalayas": HimalayasAdapter,
    "hn_hiring": HNHiringAdapter,
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "google_alerts": GoogleAlertsAdapter,
}
