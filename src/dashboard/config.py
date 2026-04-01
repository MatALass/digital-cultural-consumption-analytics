from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / 'data'
RAW_BAROMETER_PATH = DATA_DIR / 'raw' / '2024-barometre-consommation.xlsx'
DATAMAP_PATH = DATA_DIR / 'raw' / '2024-datamap.xlsx'
PROCESSED_DATA_PATH = DATA_DIR / 'processed' / 'data.xlsx'
ANALYTICS_EXPORT_PATH = DATA_DIR / 'processed' / 'analytics_dataset_generated.csv'
MODULE_INVENTORY_PATH = DATA_DIR / 'processed' / 'raw_module_inventory.csv'
DATAMAP_EXCERPT_PATH = DATA_DIR / 'processed' / 'datamap_module_excerpt.csv'

PAGE_TITLE = 'Digital Cultural Consumption Analytics'
PAGE_ICON = '🎧'
DEFAULT_LAYOUT = 'wide'

PROCESSED_COLUMN_RENAMES = {
    'sexe': 'sex',
    'age': 'age',
    'region': 'region',
    'type_agglomeration': 'agglomeration_type',
    'situation_personnelle': 'personal_situation',
    'profession_principale': 'main_profession',
    'statut_emploi': 'employment_status',
    'frequence_internet': 'internet_frequency',
    'frequence_conso_culturelle': 'cultural_frequency',
    'type_conso_legale_ou_illegale': 'legality_type',
    'evolution_conso_legale': 'legality_evolution',
    'gratuit_ou_payant': 'payment_type',
    'depense_mensuelle_culturelle': 'monthly_spending',
    'appareils_conso_films_series': 'devices_films_series',
    'utilisation_vpn': 'vpn_usage',
    'utilisation_applis_crackees': 'cracked_apps_usage',
    'utilisation_telechargement_streaming': 'streaming_download_type',
    'reglages_dns': 'dns_settings_usage',
    'acces_services_payants': 'paid_services_access',
    'taille_foyer': 'household_size',
    'nb_enfants': 'children_count',
    'statut_foyer': 'household_status',
}

AGE_GROUP_BINS = [0, 24, 34, 49, 64, 120]
AGE_GROUP_LABELS = ['18-24', '25-34', '35-49', '50-64', '65+']

INTERNET_FREQUENCY_SCORE = {
    'Moins souvent': 1,
    '1 fois par mois': 2,
    '2 à 3 fois par mois': 3,
    '1 à 2 fois par semaine': 4,
    '3 à 5 fois par semaine': 5,
    '1 fois par jour ou presque': 6,
    'Plusieurs fois par jour': 7,
}

CULTURAL_FREQUENCY_SCORE = {
    'Moins souvent': 1,
    '1 à 3 fois par mois': 2,
    '1 à 5 fois par semaine': 3,
    'Tous les jours ou presque': 4,
}

LEGALITY_SCORE = {
    'Légale': 1,
    'Souvent légale': 2,
    'Autant': 3,
    'Souvent illégale': 4,
    'Illégale': 5,
}

PAYMENT_SCORE = {
    'gratuit': 1,
    'souvent gratuit': 2,
    'autant': 3,
    'souvent payante': 4,
    'payante': 5,
}

VPN_SCORE = {
    'jamais': 0,
    'ancien utilisateur': 1,
    'occasionnellement': 2,
    'régulièrement': 3,
}

DNS_SCORE = {
    'Je ne sais pas ce que c’est': 0,
    'Jamais': 0,
    'De temps en temps': 1,
    'Régulièrement': 2,
}

PAID_ACCESS_SCORE = {
    'Non': 0,
    'compte partagé': 1,
    'abonné': 2,
}

DOWNLOAD_RISK_SCORE = {
    'Gratuit': 3,
    'souvent gratuit': 2,
    'Autant': 1,
    'souvent payante': 0,
    'payante': 0,
}

RAW_MODULE_PATTERNS = {
    'qbu1_paid_matrix': r'^QBU1_r\d+$',
    'qbu5a_devices': r'^QBU5a_r\d+_c\d+$',
    'qbu10a_illegal_means': r'^QBU10a_\d+$',
    'qbu10b_illegal_means': r'^QBU10b_\d+$',
    'qbu10c_illegal_means': r'^QBU10c_\d+$',
    'qbu10d_illegal_means': r'^QBU10d_\d+$',
    'qbu11_illegal_frequency': r'^QBU11_r\d+$',
    'qbu11b_illicit_methods': r'^QBU11B_r\d+_c\d+$',
    'qbu12_stream_ripping': r'^QBU12_r\d+$',
    'qbol3_legal_advantages': r'^QBOL3_\d+$',
    'qbol4_legal_motivations': r'^QBOL4_\d+$',
}

CHART_HEIGHT = 420

PALETTE_SEGMENT = {
    'Premium Legal Users': '#00CC96',
    'Hybrid Monetizers': '#AB63FA',
    'Heavy Free Users': '#FFA15A',
    'Risk-Oriented Free Users': '#EF553B',
    'Casual Value Seekers': '#636EFA',
    'Low Engagement Users': '#7F7F7F',
}

PALETTE_GENERATION = {
    'Gen Z': '#636EFA',
    'Millennial': '#00CC96',
    'Gen X': '#FFA15A',
    'Boomer+': '#AB63FA',
    'Unknown': '#7F7F7F',
}

PALETTE_VALUE_TIER = {
    'Non-spender': '#B6C2CF',
    'Low spender': '#7DCFB6',
    'Mid spender': '#00A896',
    'High spender': '#028090',
    'Top spender': '#05668D',
}

PALETTE_ACCESS_STYLE = {
    'Legal Paid': '#00CC96',
    'Legal Free': '#19D3F3',
    'Hybrid': '#AB63FA',
    'Risk Heavy': '#EF553B',
    'Unspecified': '#7F7F7F',
}

PAGES = {
    '📌 Executive Overview': 'overview',
    '👥 Audience & Context': 'audience',
    '🛜 Behavior & Access': 'behavior',
    '💸 Monetization': 'monetization',
    '🧩 Raw Modules': 'raw_modules',
    '🎯 Segmentation': 'segmentation',
    '🔎 Survey Explorer': 'survey_explorer',
    '🧪 Methodology': 'methodology',
}
